output "dynamodb_table_name" {
  value = aws_dynamodb_table.trackwise_records.name
}
output "http_api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}
output "ec2_instance_id" {
  value = aws_instance.chatbot_server.id
}

output "ec2_public_ip" {
  value = aws_instance.chatbot_server.public_ip
}

output "ssh_connection_command" {
  description = "Command to SSH into the EC2 instance"
  value       = "ssh -i trackwise-chatbot-key.pem ec2-user@${aws_instance.chatbot_server.public_ip}"
}

