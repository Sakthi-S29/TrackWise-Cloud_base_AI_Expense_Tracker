import json
import boto3
import requests
import logging
from requests_aws4auth import AWS4Auth
from datetime import datetime

# --- Setup logging ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = "us-east-1"
service = "es"
bucket_name = "trackwise-vector-cache"
s3_key = "texts.json"
opensearch_url = "https://search-transaction-vectore-store-3sxh5zsi2y7pzl5a3ytfb2unri.us-east-1.es.amazonaws.com/transactions/_doc"

# AWS Clients
bedrock = boto3.client("bedrock-runtime", region_name=region)
s3 = boto3.client("s3")
credentials = boto3.Session().get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

def lambda_handler(event, context):
    try:
        # Auth check
        headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        token = headers.get("authorization")
        if token != "Bearer sakthi-2025-trackwise-token":
            return { "statusCode": 401, "body": "Unauthorized" }

        body = json.loads(event["body"])
        record_id = body["id"]
        amount = float(body["amount"])
        date = body["date"]
        vendor = body.get("vendor", "Unknown Vendor")
        category = body.get("category", "Uncategorized")
        description = body.get("description", "")
        type_ = body["type"]  # "income" or "expense"
        timestamp = datetime.strptime(date, "%Y-%m-%d").isoformat()

        # Line items summary
        line_items = body.get("line_items", [])
        item_list = [f"{item.get('item', '')} (${item.get('amount', 0)})" for item in line_items]
        items_summary = ", ".join(item_list)

        # Human-style natural summary text
        if type_.lower() == "income":
            text = (
                f"On {date}, you received an income of ${amount} from {vendor}, categorized as {category}."
                f" Description: {description}."
            )
        else:
            if items_summary:
                text = (
                    f"On {date}, you spent ${amount} at {vendor} on items such as {items_summary}, categorized under {category}."
                    f" Description: {description}."
                )
            else:
                text = (
                    f"On {date}, you made a payment of ${amount} at {vendor}, categorized under {category}."
                    f" Description: {description}."
                )

        logger.info("🧠 Final constructed text: %s", text)

        # Step 1: Generate Titan embedding
        bedrock_response = bedrock.invoke_model(
            body=json.dumps({"inputText": text}),
            modelId="amazon.titan-embed-text-v2:0",
            accept="application/json",
            contentType="application/json"
        )
        embedding = json.loads(bedrock_response["body"].read())["embedding"]
        logger.info("📐 Embedding vector length: %d", len(embedding))

        # Step 2: Store in OpenSearch
        doc = {
            "id": record_id,
            "text": text,
            "embedding": embedding,
            "amount": amount,
            "date": date,
            "timestamp": timestamp,
            "vendor": vendor,
            "category": category,
            "type": type_,
            "line_items_raw": items_summary
        }

        logger.info("📦 Document to be indexed in OpenSearch: %s", json.dumps(doc))

        os_response = requests.post(
            opensearch_url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            data=json.dumps(doc)
        )

        logger.info("🔍 OpenSearch status code: %d", os_response.status_code)
        logger.info("🔎 OpenSearch response: %s", os_response.text)

        if not os_response.ok:
            raise Exception(f"Failed to index to OpenSearch: {os_response.text}")

        # Step 3: Append to S3 texts.json
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
            texts = json.loads(obj['Body'].read())
        except s3.exceptions.NoSuchKey:
            texts = []

        texts.append(doc)

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(texts),
            ContentType="application/json"
        )

        logger.info("✅ Successfully updated texts.json in S3.")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "✅ Indexed and updated texts.json successfully."})
        }

    except Exception as e:
        logger.error("❌ Error during Lambda execution: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
