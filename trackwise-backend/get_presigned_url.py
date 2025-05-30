import json
import boto3
import uuid

s3 = boto3.client("s3")
BUCKET_NAME = "trackwise-bill-uploads"

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        filename = body.get("filename", "bill.pdf")
        unique_filename = f"{uuid.uuid4()}_{filename}"

        presigned_post = s3.generate_presigned_post(
            Bucket=BUCKET_NAME,
            Key=unique_filename,
            Fields={"acl": "private"},
            Conditions=[
                {"acl": "private"},
                ["starts-with", "$Content-Type", ""]
            ],
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "url": presigned_post["url"],
                "fields": presigned_post["fields"],
                "key": unique_filename
            })
        }

    except Exception as e:
        print("Error generating presigned URL:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": str(e)})
        }
