output "dynamodb_table_name" {
  value = aws_dynamodb_table.trackwise_records.name
}
output "http_api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}