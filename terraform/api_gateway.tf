resource "aws_apigatewayv2_api" "http_api" {
  name          = "TrackWiseHTTPAPI"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins     = ["*"] # Use "*" for testing; restrict to your frontend URL in production
    allow_methods     = ["GET", "POST", "OPTIONS"]
    allow_headers     = ["*"]
    expose_headers    = ["*"]
    max_age           = 3600
    allow_credentials = false
  }
}
