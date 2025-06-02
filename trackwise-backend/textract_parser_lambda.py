import json
import boto3
from decimal import Decimal
from datetime import datetime
import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("TrackWiseRecords")

EMBEDDING_API = "https://dqficiv943.execute-api.us-east-1.amazonaws.com/prod/index-embedding"
AUTH_TOKEN = "sakthi-2025-trackwise-token"

def safe_decimal(value_str):
    try:
        return Decimal(value_str.replace("$", "").replace(",", "").strip())
    except:
        return Decimal("0")

def notify_embedding(record):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AUTH_TOKEN}"
        }
        res = requests.post(EMBEDDING_API, json=record, headers=headers)
        print("Embedding API response:", res.status_code, res.text)
    except Exception as e:
        print("Failed to notify embedding service:", str(e))

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        document = event['Records'][0]['s3']['object']['key']

        textract = boto3.client('textract')
        response = textract.analyze_expense(
            Document={'S3Object': {'Bucket': bucket, 'Name': document}}
        )
        doc = response['ExpenseDocuments'][0]

        summary = {}
        for field in doc.get('SummaryFields', []):
            label = field.get('Type', {}).get('Text')
            value = field.get('ValueDetection', {}).get('Text')
            if label and value:
                summary[label.upper()] = value

        total_candidates = []
        for key in ["TOTAL", "SUBTOTAL", "AMOUNT_DUE", "BALANCE", "AMOUNT"]:
            if key in summary:
                total_candidates.append(safe_decimal(summary[key]))

        if not total_candidates:
            for val in summary.values():
                try:
                    total_candidates.append(safe_decimal(val))
                except:
                    continue

        amount = max(total_candidates) if total_candidates else Decimal("0")

        line_items = []
        for group in doc.get('LineItemGroups', []):
            for item in group.get('LineItems', []):
                fields = {
                    f.get('Type', {}).get('Text'): f.get('ValueDetection', {}).get('Text')
                    for f in item.get('LineItemExpenseFields', [])
                }
                line_items.append({
                    "item": fields.get("ITEM", ""),
                    "amount": safe_decimal(fields.get("PRICE", "0")),
                    "category": "Uncategorized"
                })

        record = {
            "id": document,
            "type": "expense",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "category": "AutoParsed",
            "description": summary.get("VENDOR_NAME", "Bill"),
            "vendor": summary.get("VENDOR_NAME", ""),
            "line_items": line_items,
            "source": "textract"
        }

        table.put_item(Item=record)

        # Notify personal AWS embedding Lambda
        notify_embedding(record)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Parsed and stored successfully"})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
