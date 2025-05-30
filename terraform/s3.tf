# s3.tf
resource "aws_s3_bucket" "bill_uploads" {
  bucket = "trackwise-bill-uploads"
  force_destroy = true
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.bill_uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.textract_parser.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowS3InvokeTextractParser"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.textract_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.bill_uploads.arn
}
