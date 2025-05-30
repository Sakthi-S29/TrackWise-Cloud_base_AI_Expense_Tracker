import json
from decimal import Decimal
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TrackWiseRecords')

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
            "vendor": body.get("vendor", "")
        }

        table.put_item(Item=item)

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
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # <-- ADD THIS ON ERRORS TOO
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
