resource "aws_lambda_function" "get_transactions" {
  function_name = "trackwise-get-transactions"
  handler       = "get_transactions_lambda.lambda_handler"
  runtime       = "python3.11"
  role          = "arn:aws:iam::570322492335:role/LabRole"

  filename         = "${path.module}/../trackwise-backend/get_transactions_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../trackwise-backend/get_transactions_lambda.zip")
  timeout          = 10
}

resource "aws_apigatewayv2_integration" "get_transactions" {
  api_id                  = aws_apigatewayv2_api.http_api.id
  integration_type        = "AWS_PROXY"
  integration_uri         = aws_lambda_function.get_transactions.invoke_arn
  integration_method      = "POST"  # Must be POST even for GET route
  payload_format_version  = "2.0"
}

resource "aws_apigatewayv2_route" "get_transactions" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /get-transactions"  # The route key seen by the frontend
  target    = "integrations/${aws_apigatewayv2_integration.get_transactions.id}"
}

resource "aws_lambda_permission" "get_transactions" {
  statement_id  = "AllowGetTransactionsInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_transactions.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
