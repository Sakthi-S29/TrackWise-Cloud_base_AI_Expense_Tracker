resource "aws_apigatewayv2_api" "http_api" {
  name          = "TrackWiseAPI"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
    expose_headers = ["*"]
    max_age = 3600
  }
}
