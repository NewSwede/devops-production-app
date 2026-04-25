variable "admin_cidr_block" {
  description = "CIDR block allowed to access the instance over SSH."
  type        = string
  default     = "88.164.7.207/32"
}

variable "ssh_key_name" {
  description = "AWS EC2 key pair name to create and attach to the instance."
  type        = string
  default     = "devops-key-terraform"
}

variable "ssh_public_key_path" {
  description = "Path to the local public key used to create the AWS key pair."
  type        = string
}

variable "ssh_private_key_path" {
  description = "Path to the local private key used in the generated SSH command output."
  type        = string
}
