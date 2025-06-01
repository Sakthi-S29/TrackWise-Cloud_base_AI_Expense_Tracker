import json
import os
import faiss
import boto3
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# Config
BUCKET_NAME = "trackwise-chatbot-vectors"
INDEX_FILE = "faiss_index.index"
TEXT_FILE = "texts.json"
MODEL_PATH = "/home/ec2-user/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LOCAL_INDEX = "/tmp/faiss_index.index"
LOCAL_TEXTS = "/tmp/texts.json"

# AWS
session = boto3.Session(region_name="us-east-1")
s3 = session.client("s3")

# Flask app
app = Flask(__name__)

# Step 1: Download FAISS index + texts.json from S3
print("Downloading FAISS index and texts.json from S3...")
s3.download_file(BUCKET_NAME, INDEX_FILE, LOCAL_INDEX)
s3.download_file(BUCKET_NAME, TEXT_FILE, LOCAL_TEXTS)
print("Download complete.")

# Step 2: Load index and texts
index = faiss.read_index(LOCAL_INDEX)
with open(LOCAL_TEXTS) as f:
    record_texts = json.load(f)

# Step 3: Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Step 4: Load LLaMA model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=1024,
    n_threads=4,
    n_gpu_layers=20,
    verbose=False
)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    query = data.get("query", "")

    # Embed query
    query_vec = embedder.encode([query])
    D, I = index.search(np.array(query_vec).astype("float32"), k=3)

    # Select top records
    context_chunks = [record_texts[i] for i in I[0] if i < len(record_texts)]
    context = "\n".join(f"- {c}" for c in context_chunks)

    # Prompt
    prompt = f"""You are a helpful financial assistant. Based on the user's transaction records below, answer the question accurately.

Records:
{context}

Question: {query}
Answer:"""

    # Generate response
    response = llm(prompt, max_tokens=256, stop=["\nUser:", "\nQuestion:"])

    return jsonify({
        "query": query,
        "answer": response["choices"][0]["text"].strip()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


