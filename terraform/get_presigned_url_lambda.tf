resource "aws_lambda_function" "get_presigned_url" {
  function_name = "trackwise-get-presigned-url"
  handler       = "get_presigned_url.lambda_handler"
  runtime       = "python3.11"
  role          = "arn:aws:iam::570322492335:role/LabRole"
  filename         = "${path.module}/../trackwise-backend/get_presigned_url.zip"
  source_code_hash = filebase64sha256("${path.module}/../trackwise-backend/get_presigned_url.zip")
  timeout          = 10
}

resource "aws_apigatewayv2_integration" "get_presigned_url" {
  api_id                = aws_apigatewayv2_api.http_api.id
  integration_type      = "AWS_PROXY"
  integration_uri       = aws_lambda_function.get_presigned_url.invoke_arn
  integration_method    = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_presigned_url" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /get-presigned-url"
  target    = "integrations/${aws_apigatewayv2_integration.get_presigned_url.id}"
}

resource "aws_lambda_permission" "allow_invoke_presign" {
  statement_id  = "AllowInvokePresign"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_presigned_url.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
