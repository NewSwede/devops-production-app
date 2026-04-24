output "public_ip" {
  value = aws_instance.app.public_ip
}

output "ssh_command" {
  value = "ssh -i \"D:/Users/sylva/keys/devops-key.pem\" ubuntu@${aws_instance.app.public_ip}"
}