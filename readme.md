Here’s a polished `README.md` written from a **third-person user perspective** — as if guiding another developer who is **new to the project**. It's beginner-friendly, detailed, and structured for GitHub:

---

```markdown
# 📊 TrackWise – AI-Powered Expense Tracker with Bill Scanning and Chatbot

**TrackWise** is a cloud-native, serverless expense tracking application designed to simplify financial management. It enables users to add expenses manually or by uploading bills, and features a chatbot that provides intelligent financial insights using Amazon Bedrock and OpenSearch.

---

## 🧩 Key Features

- **Manual Income/Expense Entry**
- **AI Bill Parsing** via AWS Textract
- **Chatbot Q&A** over financial records using LLMs
- **Persistent Storage** with DynamoDB
- **Searchable Vector Store** with OpenSearch
- **Fully Serverless Deployment** via Terraform
- **CI-style Automation Script** for deployment

---

## 🏗️ Tech Stack

| Layer         | Technology |
|---------------|------------|
| Frontend      | React, Vite, Tailwind |
| Backend       | Python (Lambda via FastAPI-style handlers) |
| Embedding     | Amazon Bedrock Titan |
| LLM Chatbot   | Claude (Bedrock) |
| Storage       | S3, DynamoDB |
| Search        | OpenSearch with KNN |
| IaC           | Terraform |
| Deployment    | Bash scripts for automation |

---

## 📁 Repository Structure

```

TrackWise/
├── terraform/                        # Learner Lab Terraform (frontend, backend, DynamoDB)
├── trackwise-backend/               # Lambda Python files and zips
├── trackwise-frontend/              # React app source
├── trackwise-embedding/terraform/   # Personal AWS account infra (OpenSearch, Bedrock)
├── deploy-all.sh                    # Complete automated deployment script
└── README.md

````

---

## 🚀 Getting Started (Setup & Deployment)

This section assumes the developer has:

- Access to **two AWS accounts**:
  - **Personal AWS**: Used for OpenSearch and Bedrock
  - **Learner Lab AWS**: Used for app deployment (Textract, S3, Lambdas)
- AWS CLI configured
- Terraform installed
- GitHub project cloned locally

---

### 🔐 Step 1: Export AWS Credentials

**Personal Account:**

```bash
export AWS_ACCESS_KEY_ID=<your_personal_key>
export AWS_SECRET_ACCESS_KEY=<your_personal_secret>
````

**Learner Lab Account (Temporary credentials):**

```bash
export AWS_ACCESS_KEY_ID=<lab_key>
export AWS_SECRET_ACCESS_KEY=<lab_secret>
export AWS_SESSION_TOKEN=<lab_token>
```

---

### 🛠️ Step 2: Provision AI Infrastructure (Personal Account)

Navigate to the embedding Terraform folder:

```bash
cd trackwise-embedding/terraform
terraform init
terraform apply -auto-approve
```

This sets up:

* OpenSearch domain
* Titan embedding API (`/index-embedding`)
* Claude LLM API (`/semantic-search`)
* API Gateway and Lambda integration

> ⚠️ If `semantic-search` is not directly in outputs, just replace `index-embedding` with `semantic-search`.

---

### ⚙️ Step 3: Run Full App Deployment

Return to the project root and run the automated script:

```bash
bash deploy-all.sh
```

This script will:

1. Extract the AI URLs from personal Terraform output
2. Inject them into the manual entry and Textract parser Lambda code
3. Zip and prepare Lambda code
4. Switch to Learner Lab AWS credentials
5. Apply Learner Lab Terraform (API Gateway, DynamoDB, Textract, etc.)
6. Inject API Gateway URL into the React frontend
7. Build and deploy the frontend to S3

---

## 🌐 Accessing the Application

Once deployed, the script prints:

```bash
Frontend available at: http://trackwise-frontend-XXXXXX.s3-website-us-east-1.amazonaws.com
```

> The app includes manual entry, bill upload, and chatbot modules.

---

## 🤖 Bedrock & OpenSearch Configuration

### ✅ Enabling Bedrock Models

Ensure these models are enabled via the [Bedrock Console](https://console.aws.amazon.com/bedrock/):

* Titan Embeddings v2 (for vector generation)
* Claude v2/v3 Sonnet (for natural language responses)

### 🔍 OpenSearch Index Structure

The `transactions` index uses:

```json
{
  "embedding": { "type": "knn_vector", "dimension": 1536 },
  "text": { "type": "text" },
  "metadata": { "type": "object" }
}
```

---

## 🧹 Maintenance Tips

### 💬 Clearing OpenSearch Index (Optional)

If vector search needs to be reset:

```json
POST transactions/_delete_by_query
{
  "query": {
    "match_all": {}
  }
}
```

Or flush cache:

```bash
POST transactions/_flush
```

---

## 🧠 Chatbot Queries (Examples)

* "How much did I spend on groceries last week?"
* "List all food expenses from May."
* "Total income this month?"

The chatbot uses embedded queries + Claude LLM to answer based on OpenSearch-matched records.

---

## 🔒 Security Recommendations

* Avoid committing your AWS secrets in Git
* Use `.env` or AWS Secrets Manager for production
* Lock down S3 buckets if not using for static site hosting

---

## 🖼️ Screenshots (Add After Deployment)

```
![Home Page](docs/screenshot_home.png)
![Bill Upload](docs/screenshot_upload.png)
![Chatbot](docs/screenshot_chatbot.png)
```

---

## ✨ Future Enhancements

* Cognito-based login
* Custom query dashboard with analytics
* Batch re-embedding support
* CloudWatch + SNS alerts for cost control

---

## 👨‍💻 Author

* **Sakthi Sharan Mahadevan** – Developer, Architect, and AWS Engineer

> Contributions welcome!

---

## 📄 License

MIT License – Free to use, modify, and deploy.

```

Let me know if you want a `docs/` folder with starter screenshots, logo badge, or a `.gitignore` and `.env.sample` file!
```
