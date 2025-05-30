resource "aws_s3_bucket" "bill_uploads" {
  bucket = "trackwise-bill-uploads"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "block_public_access" {
  bucket = aws_s3_bucket.bill_uploads.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "bill_uploads_cors" {
  bucket = aws_s3_bucket.bill_uploads.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = aws_s3_bucket.bill_uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.textract_parser.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3ToInvokeTextractParser"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.textract_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bill_uploads.arn
}
