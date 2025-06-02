resource "aws_lambda_function" "chatbot_query_handler" {
  function_name = "trackwise-chatbot-query"
  handler       = "chatbot_query_handler.lambda_handler"
  runtime       = "python3.11"
  role          = "arn:aws:iam::570322492335:role/LabRole"

  filename         = "${path.module}/../trackwise-backend/chatbot_query_handler.zip"
  source_code_hash = filebase64sha256("${path.module}/../trackwise-backend/chatbot_query_handler.zip")
  timeout          = 20
  memory_size      = 512
}

resource "aws_apigatewayv2_integration" "chatbot_query" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.chatbot_query_handler.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "chatbot_query" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /chat-query"
  target    = "integrations/${aws_apigatewayv2_integration.chatbot_query.id}"
}

resource "aws_lambda_permission" "chatbot_query" {
  statement_id  = "AllowChatbotQueryInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chatbot_query_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
