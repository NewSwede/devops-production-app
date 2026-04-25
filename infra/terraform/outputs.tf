output "public_ip" {
  value = aws_instance.app.public_ip
}

output "ssh_command" {
  value = "ssh -i \"${var.ssh_private_key_path}\" ubuntu@${aws_instance.app.public_ip}"
}
