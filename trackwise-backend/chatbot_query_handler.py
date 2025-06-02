import json
import requests

PERSONAL_API_URL = "https://dqficiv943.execute-api.us-east-1.amazonaws.com/prod/semantic-search"
AUTH_TOKEN = "Bearer sakthi-2025-trackwise-token"

def lambda_handler(event, context):
    try:
        print("Incoming event:", event)

        body = json.loads(event["body"])
        query = body.get("query")

        if not query:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "Missing 'query'"})
            }

        payload = { "query": query }
        headers = {
            "Authorization": AUTH_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.post(PERSONAL_API_URL, json=payload, headers=headers)
        print("Personal API response:", response.status_code, response.text)

        return {
            "statusCode": response.status_code,
            "headers": cors_headers(),
            "body": response.text
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "*"
    }
