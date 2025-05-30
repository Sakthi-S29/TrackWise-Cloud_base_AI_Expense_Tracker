resource "aws_lambda_function" "manual_entry" {
  function_name = "trackwise-manual-entry"
  handler       = "manual_entry_lambda.lambda_handler"
  runtime       = "python3.11"
  role          = "arn:aws:iam::570322492335:role/LabRole"

  filename         = "${path.module}/../trackwise-backend/manual_entry_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../trackwise-backend/manual_entry_lambda.zip")
  timeout          = 10
}

resource "aws_apigatewayv2_integration" "manual_entry" {
  api_id                = aws_apigatewayv2_api.http_api.id
  integration_type      = "AWS_PROXY"
  integration_uri       = aws_lambda_function.manual_entry.invoke_arn
  integration_method    = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "manual_entry" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /manual-entry"
  target    = "integrations/${aws_apigatewayv2_integration.manual_entry.id}"
}

resource "aws_lambda_permission" "manual_entry" {
  statement_id  = "AllowManualEntryInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.manual_entry.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}
