provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "embedding_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "embedding_lambda_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["logs:*"],
        Effect = "Allow",
        Resource = "*"
      },
      {
        Action = ["bedrock:InvokeModel"],
        Effect = "Allow",
        Resource = "*"
      },
      {
        Action = [
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpGet"
        ],
        Effect = "Allow",
        Resource = "arn:aws:es:us-east-1:248189918645:domain/transaction-vectore-store/*"
      },
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Effect = "Allow",
        Resource = "arn:aws:s3:::trackwise-vector-cache/texts.json"
      },
      {
        Action = ["s3:ListBucket"],
        Effect = "Allow",
        Resource = "arn:aws:s3:::trackwise-vector-cache"
      }
    ]
  })
}


resource "aws_lambda_function" "embedder" {
  function_name    = "TrackwiseEmbedder"
  filename         = "../lambda/index_embedder.zip"
  source_code_hash = filebase64sha256("../lambda/index_embedder.zip")
  handler          = "index_embedder.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_exec_role.arn
  timeout          = 60
  memory_size      = 512
}

resource "aws_apigatewayv2_api" "embedding_api" {
  name          = "EmbeddingAPI"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.embedding_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.embedder.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "embedding_route" {
  api_id    = aws_apigatewayv2_api.embedding_api.id
  route_key = "POST /index-embedding"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "allow_api" {
  statement_id  = "AllowInvokeByAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.embedder.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.embedding_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.embedding_api.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_lambda_function" "semantic_search_handler" {
  function_name    = "semantic_search_handler"
  filename         = "../lambda/semantic_search_handler.zip"
  source_code_hash = filebase64sha256("../lambda/semantic_search_handler.zip")
  handler          = "semantic_search_handler.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_exec_role.arn
  timeout          = 30
  memory_size      = 512
}

resource "aws_apigatewayv2_integration" "semantic_integration" {
  api_id                 = aws_apigatewayv2_api.embedding_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.semantic_search_handler.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "semantic_route" {
  api_id    = aws_apigatewayv2_api.embedding_api.id
  route_key = "POST /semantic-search"
  target    = "integrations/${aws_apigatewayv2_integration.semantic_integration.id}"
}

resource "aws_lambda_permission" "allow_semantic_api" {
  statement_id  = "AllowSemanticQueryInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.semantic_search_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.embedding_api.execution_arn}/*/*"
}

resource "aws_s3_bucket" "vector_cache" {
  bucket = "trackwise-vector-cache"

  tags = {
    Name        = "TrackWise Vector Cache"
    Environment = "production"
  }
}

resource "aws_s3_bucket_public_access_block" "vector_cache_block" {
  bucket                  = aws_s3_bucket.vector_cache.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "vector_cache_versioning" {
  bucket = aws_s3_bucket.vector_cache.id

  versioning_configuration {
    status = "Enabled"
  }
}
