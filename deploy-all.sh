#!/bin/bash
set -e

echo "🚀 Starting Learner Lab deployment..."

### === STEP 1: Extract API URLs from personal Terraform output ===
echo "🔍 Extracting embedding & semantic API URLs from personal account output..."
EMBEDDING_API=$(terraform -chdir=trackwise-embedding/terraform output -raw embedding_api_url)
SEMANTIC_API=$(echo "$EMBEDDING_API" | sed 's|/index-embedding$|/semantic-search|')

echo "✅ EMBEDDING_API = $EMBEDDING_API"
echo "✅ SEMANTIC_API = $SEMANTIC_API"

### === STEP 2: Inject API URLs into Lambda files ===
echo "✍️ Injecting into Lambda files..."
sed -i '' "s|^EMBEDDING_API = .*|EMBEDDING_API = \"$EMBEDDING_API\"|" trackwise-backend/manual_entry_lambda.py
sed -i '' "s|^EMBEDDING_API = .*|EMBEDDING_API = \"$EMBEDDING_API\"|" trackwise-backend/textract_parser_lambda.py
sed -i '' "s|^PERSONAL_API_URL = .*|PERSONAL_API_URL = \"$SEMANTIC_API\"|" trackwise-backend/chatbot_query_handler.py

### === STEP 3: Zip updated Lambda files ===
echo "📦 Zipping Lambda files..."
cd trackwise-backend
zip -r manual_entry_lambda.zip manual_entry_lambda.py
zip -r textract_parser_lambda.zip textract_parser_lambda.py
zip -r chatbot_query_handler.zip chatbot_query_handler.py
cd ..

### === STEP 4: Set Learner Lab AWS credentials ===
echo "🔐 Switching to Learner Lab AWS credentials..."
source .env
### === STEP 5: Apply Terraform in Learner Lab ===
echo "🌍 Applying Terraform for Learner Lab..."
terraform -chdir=terraform apply -auto-approve

### === STEP 6: Extract backend API URL ===
echo "🌐 Extracting backend API URL for frontend..."
API_URL=$(terraform -chdir=terraform output -raw http_api_endpoint)
S3_BUCKET=$(aws s3api list-buckets --query "Buckets[?contains(Name, 'trackwise-frontend')].Name" --output text)

### === STEP 7: Inject into frontend .env and build ===
echo "✍️ Creating .env.production for frontend..."
cat > trackwise-frontend/.env.production <<EOF
VITE_API_BASE_URL=$API_URL
EOF
echo "✅ Injected VITE_API_BASE_URL=$API_URL"

echo "🧱 Building frontend..."
cd trackwise-frontend
rm -rf dist
npm install
npm run build
cd ..

### === STEP 8: Deploy frontend to S3 ===
echo "🚢 Uploading frontend to S3: $S3_BUCKET"
aws s3 sync trackwise-frontend/dist s3://$S3_BUCKET --delete --exact-timestamps

echo "🎉 Learner Lab deployment complete!"
echo "🌍 Frontend available at: http://$S3_BUCKET.s3-website-us-east-1.amazonaws.com"
