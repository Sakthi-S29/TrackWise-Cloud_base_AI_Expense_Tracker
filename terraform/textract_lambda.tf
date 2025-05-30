resource "aws_lambda_function" "textract_parser" {
  function_name = "trackwise-textract-parser"
  handler       = "textract_parser_lambda.lambda_handler"
  runtime       = "python3.11"
  role          = "arn:aws:iam::570322492335:role/LabRole"

  filename         = "${path.module}/../trackwise-backend/textract_parser_lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/../trackwise-backend/textract_parser_lambda.zip")
  timeout          = 15
}
