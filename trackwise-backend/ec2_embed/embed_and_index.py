import boto3
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# AWS setup
session = boto3.Session(region_name="us-east-1")
dynamodb = session.resource('dynamodb')
s3 = session.client('s3')
table = dynamodb.Table('TrackWiseRecords')

# Config
BUCKET_NAME = 'trackwise-chatbot-vectors'
INDEX_FILE = 'faiss_index.index'
TEXT_FILE = 'texts.json'

# Step 1: Fetch DynamoDB records
def fetch_records():
    response = table.scan()
    records = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        records.extend(response['Items'])
    return records

# Step 2: Convert records to searchable texts
def build_text_chunks(records):
    texts = []
    for r in records:
        summary = f"{r.get('type')} of ${r.get('amount')} on {r.get('date')}"
        vendor = r.get('vendor', '')
        category = r.get('category', '')
        desc = r.get('description', '')
        line_items = r.get("line_items", [])

        item_lines = ""
        for item in line_items:
            item_name = item.get("item", "")
            item_amount = item.get("amount", "")
            item_lines += f" Item: {item_name} (${item_amount})."

        full_text = f"{summary}. Vendor: {vendor}. Category: {category}. Note: {desc}.{item_lines}"
        texts.append(full_text)
    return texts

# Step 3: Embed and upload
def create_and_upload_faiss_index():
    records = fetch_records()
    texts = build_text_chunks(records)

    print(f"Embedding {len(texts)} records...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index and texts locally
    faiss.write_index(index, INDEX_FILE)
    with open(TEXT_FILE, "w") as f:
        json.dump(texts, f)

    # Upload to S3
    s3.upload_file(INDEX_FILE, BUCKET_NAME, INDEX_FILE)
    s3.upload_file(TEXT_FILE, BUCKET_NAME, TEXT_FILE)

    print(f"Uploaded {INDEX_FILE} and {TEXT_FILE} to S3 bucket '{BUCKET_NAME}'")

if __name__ == "__main__":
    create_and_upload_faiss_index()
