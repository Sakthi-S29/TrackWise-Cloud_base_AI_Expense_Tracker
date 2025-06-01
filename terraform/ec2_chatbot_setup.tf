
# VPC
resource "aws_vpc" "chatbot_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "chatbot-vpc" }
}

# Subnet
resource "aws_subnet" "chatbot_subnet" {
  vpc_id                  = aws_vpc.chatbot_vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "us-east-1a"
  tags = { Name = "chatbot-subnet" }
}

# Internet Gateway
resource "aws_internet_gateway" "chatbot_igw" {
  vpc_id = aws_vpc.chatbot_vpc.id
  tags = { Name = "chatbot-igw" }
}

# Route Table
resource "aws_route_table" "chatbot_rt" {
  vpc_id = aws_vpc.chatbot_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.chatbot_igw.id
  }

  tags = { Name = "chatbot-rt" }
}

# Route Table Association
resource "aws_route_table_association" "chatbot_rta" {
  subnet_id      = aws_subnet.chatbot_subnet.id
  route_table_id = aws_route_table.chatbot_rt.id
}

# Security Group
resource "aws_security_group" "chatbot_sg" {
  name        = "chatbot-sg"
  description = "Allow SSH and HTTP"
  vpc_id      = aws_vpc.chatbot_vpc.id

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP access"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "chatbot-sg" }
}

# EC2 Instance
resource "aws_instance" "chatbot_server" {
  ami                    = "ami-0953476d60561c955" # Amazon Linux 2 (us-east-1)
  instance_type          = "m5.large"
  subnet_id              = aws_subnet.chatbot_subnet.id
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]
  iam_instance_profile = "LabInstanceProfile" # Ensure this IAM role exists with necessary permissions
  key_name               = "trackwise-chatbot-key"

    root_block_device {
    volume_size = 30
    volume_type = "gp2"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y git python3
              pip3 install --upgrade pip
              pip3 install faiss-cpu boto3 sentence-transformers flask
              echo "Chatbot setup complete" > /home/ec2-user/setup_status.txt
              EOF

  tags = {
    Name = "chatbot-ec2"
  }
}
