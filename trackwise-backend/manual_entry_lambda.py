import json
from decimal import Decimal
import boto3
import uuid
import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TrackWiseRecords')

EMBEDDING_API = "https://dqficiv943.execute-api.us-east-1.amazonaws.com/prod/index-embedding"
AUTH_TOKEN = "sakthi-2025-trackwise-token"

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
        body = json.loads(event['body'], parse_float=Decimal)
        record_id = str(uuid.uuid4())

        item = {
            "id": record_id,
            "type": body["type"],
            "amount": Decimal(str(body["amount"])),
            "date": body["date"],
            "category": body["category"],
            "description": body["description"],
            "vendor": body.get("vendor", ""),
            "source": "manual"
        }

        table.put_item(Item=item)

        # Notify personal AWS embedding Lambda
        notify_embedding(item)

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            },
            "body": json.dumps({"message": "Success"})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
