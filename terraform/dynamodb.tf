resource "aws_dynamodb_table" "trackwise_records" {
  name           = "TrackWiseRecords"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name        = "TrackWiseRecords"
    Environment = "Dev"
  }
}
