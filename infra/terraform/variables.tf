variable "aws_region" {
  description = "AWS region where the infrastructure is deployed."
  type        = string
  default     = "eu-west-3"
}

variable "admin_cidr_block" {
  description = "CIDR block allowed to access the instance over SSH."
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_key_name" {
  description = "AWS EC2 key pair name to create and attach to the instance."
  type        = string
  default     = "devops-key-terraform"
}

variable "ssh_public_key_path" {
  description = "Path to the local public key used to create the AWS key pair."
  type        = string
  default     = ""
}

variable "ssh_public_key" {
  description = "Public SSH key content used to create the AWS key pair. Prefer this in CI."
  type        = string
  default     = ""
}

variable "ssh_private_key_path" {
  description = "Path to the local private key used in the generated SSH command output."
  type        = string
  default     = "~/.ssh/devops-key.pem"
}
