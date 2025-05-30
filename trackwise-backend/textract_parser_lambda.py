import json
import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("TrackWiseRecords")

def lambda_handler(event, context):
    try:
        # Extract bucket and file name
        bucket = event['Records'][0]['s3']['bucket']['name']
        document = event['Records'][0]['s3']['object']['key']

        # Analyze expense using Textract
        textract = boto3.client('textract')
        response = textract.analyze_expense(
            Document={'S3Object': {'Bucket': bucket, 'Name': document}}
        )

        doc = response['ExpenseDocuments'][0]

        # Extract summary fields
        summary = {}
        for field in doc.get('SummaryFields', []):
            label = field.get('Type', {}).get('Text')
            value = field.get('ValueDetection', {}).get('Text')
            if label and value:
                summary[label] = value

        # Parse line items
        line_items = []
        for item_group in doc.get('LineItemGroups', []):
            for item in item_group.get('LineItems', []):
                fields = {
                    f.get('Type', {}).get('Text'): f.get('ValueDetection', {}).get('Text')
                    for f in item['LineItemExpenseFields']
                }
                amount_str = fields.get("PRICE", "0").replace("$", "").replace(",", "")
                try:
                    amount = Decimal(amount_str)
                except:
                    amount = Decimal("0")

                line_items.append({
                    "item": fields.get("ITEM", ""),
                    "amount": amount,
                    "category": "Uncategorized"
                })

        # Construct record
        record = {
            "id": document,
            "type": "expense",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": Decimal(summary.get("TOTAL", "0").replace("$", "").replace(",", "")),
            "category": "AutoParsed",
            "description": summary.get("VENDOR_NAME", "Bill"),
            "vendor": summary.get("VENDOR_NAME", ""),
            "line_items": line_items,
            "source": "textract"
        }

        # Store to DynamoDB
        table.put_item(Item=record)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Parsed and stored successfully", "record": record})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
