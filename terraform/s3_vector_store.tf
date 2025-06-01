resource "aws_s3_bucket" "vector_store" {
  bucket = "trackwise-chatbot-vectors"
  force_destroy = true
  tags = {
    Name = "TrackWise Chatbot Vector Store"
  }
}

resource "aws_s3_bucket_versioning" "vector_store_versioning" {
  bucket = aws_s3_bucket.vector_store.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vector_store_encryption" {
  bucket = aws_s3_bucket.vector_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

output "vector_store_bucket_name" {
  value = aws_s3_bucket.vector_store.bucket
}
