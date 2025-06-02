output "embedding_api_url" {
  description = "Public API Gateway endpoint for embedding"
  value       = "${aws_apigatewayv2_api.embedding_api.api_endpoint}/prod/index-embedding"
}
