import json
import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("TrackWiseRecords")

def safe_decimal(value_str):
    try:
        return Decimal(value_str.replace("$", "").replace(",", "").strip())
    except:
        return Decimal("0")

def lambda_handler(event, context):
    try:
        # S3 event info
        bucket = event['Records'][0]['s3']['bucket']['name']
        document = event['Records'][0]['s3']['object']['key']

        # Analyze receipt using Textract
        textract = boto3.client('textract')
        response = textract.analyze_expense(
            Document={'S3Object': {'Bucket': bucket, 'Name': document}}
        )
        doc = response['ExpenseDocuments'][0]

        # Parse summary fields
        summary = {}
        for field in doc.get('SummaryFields', []):
            label = field.get('Type', {}).get('Text')
            value = field.get('ValueDetection', {}).get('Text')
            if label and value:
                summary[label.upper()] = value  # Normalize for easier fallback

        # Choose total amount using fallback strategy
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

        # Parse line items
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

        # Prepare record for DynamoDB
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

        # Store in DynamoDB
        table.put_item(Item=record)

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
