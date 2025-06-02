import json
import boto3
import requests
from requests_aws4auth import AWS4Auth

region = "us-east-1"
service = "es"

# AWS clients
bedrock = boto3.client("bedrock-runtime", region_name=region)
credentials = boto3.Session().get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# Constants
opensearch_url = "https://search-transaction-vectore-store-3sxh5zsi2y7pzl5a3ytfb2unri.aos.us-east-1.on.aws/transactions/_search"
claude_model_id = "anthropic.claude-instant-v1"
EXPECTED_TOKEN = "Bearer sakthi-2025-trackwise-token"

def claude_prompt(query, texts):
    context = "\n\n".join(texts)
    
    return f"""Human: You are a helpful and intelligent personal finance assistant designed to analyze and respond to users based on their past transaction history. Follow these rules:

1. Use only the provided transaction records to answer.
2. Answer clearly and concisely. If the user asks for a breakdown, list totals by category or time.
3. If the question is too vague, generic, or unrelated to personal finance or transaction data, reply with: "Sorry, I can't answer that."
4. Always be specific — if dates, categories, or vendors are mentioned, include them in your response.
5. DO NOT give advice, tips, or recommendations — only answer the user's question factually.
6. Even if the category is not explicitly mentioned in the transaction records, you can infer it based on the context provided. And categorize transactions based on the context of the records.
7. DO NOT hallucinate or assume data that is not in the transaction records.

---

Transaction Records:
{context}

---

User question: {query}

Assistant:"""


def lambda_handler(event, context):
    try:
        # Step 0: Auth check
        headers = {k.lower(): v for k, v in event.get("headers", {}).items()}
        if headers.get("authorization") != EXPECTED_TOKEN:
            return {"statusCode": 401, "body": "Unauthorized"}

        body = json.loads(event["body"])
        query = body.get("query", "").strip()

        if not query:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing 'query'"})}

        # Step 1: Embed user query
        embed_resp = bedrock.invoke_model(
            body=json.dumps({"inputText": query}),
            modelId="amazon.titan-embed-text-v2:0",
            accept="application/json",
            contentType="application/json"
        )
        embedding = json.loads(embed_resp["body"].read())["embedding"]

        # Step 2: Search OpenSearch via KNN
        search_query = {
            "size": 5,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": embedding,
                        "k": 5
                    }
                }
            }
        }

        search_resp = requests.post(
            opensearch_url,
            auth=auth,
            headers={"Content-Type": "application/json"},
            json=search_query
        )
        
        # Log the full OpenSearch response
        search_response_json = search_resp.json()
        print("OpenSearch Response:", json.dumps(search_response_json, indent=2))
        
        # Step 3: Extract matching `text` records directly
        hits = search_response_json.get("hits", {}).get("hits", [])
        matched_texts = [hit["_source"]["text"] for hit in hits if "_source" in hit and "text" in hit["_source"]]

        # Step 4: Fallback if nothing matched
        context_texts = matched_texts if matched_texts else ["There are no financial records to reference."]

        # Step 5: Generate Claude response
        final_prompt = claude_prompt(query, context_texts)

        claude_resp = bedrock.invoke_model(
            body=json.dumps({
                "prompt": final_prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.5,
                "stop_sequences": ["\n\nHuman:"]
            }),
            modelId=claude_model_id,
            accept="application/json",
            contentType="application/json"
        )

        final_answer = json.loads(claude_resp["body"].read())["completion"]

        return {
            "statusCode": 200,
            "headers": cors(),
            "body": json.dumps({
                "response": final_answer,
                "opensearch_debug": {  # Optional: include debug info in response
                    "hits_count": len(hits),
                    "first_hit": hits[0]["_source"] if hits else None
                }
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": cors(),
            "body": json.dumps({"error": str(e)})
        }

def cors():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }