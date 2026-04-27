terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"] # Canonical official Ubuntu images

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  resolved_ssh_public_key = var.ssh_public_key != "" ? var.ssh_public_key : try(file(pathexpand(var.ssh_public_key_path)), "")
}

resource "aws_security_group" "app_sg" {
  name        = "devops-app-sg"
  description = "Security group for DevOps app"

  ingress {
    description = "SSH from admin IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr_block]
  }

  ingress {
    description = "HTTP public entrypoint"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "devops-app-sg"
    Environment = "production"
    Project     = "devops-production-app"
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.devops_key.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = file("${path.module}/user_data.sh")

  tags = {
    Name        = "devops-app-terraform"
    Environment = "production"
    Project     = "devops-production-app"
  }
}

resource "aws_key_pair" "devops_key" {
  key_name   = var.ssh_key_name
  public_key = local.resolved_ssh_public_key

  lifecycle {
    precondition {
      condition     = local.resolved_ssh_public_key != ""
      error_message = "Set either ssh_public_key with the public key content or ssh_public_key_path with a valid local public key path."
    }
  }
}
