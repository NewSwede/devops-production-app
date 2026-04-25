# Terraform

This directory provisions a small AWS EC2 deployment for the application.

## Files

* `main.tf`: EC2 instance, security group, and SSH key pair resources
* `variables.tf`: portable input variables for SSH access and admin CIDR
* `outputs.tf`: instance IP and ready-to-use SSH command
* `user_data.sh`: bootstrap script that installs Docker and starts the app

## Usage

1. Copy the example file:

```bash
cp terraform.tfvars.example terraform.tfvars
```

2. Edit `terraform.tfvars` with your local key paths and your admin IP CIDR.

3. Run Terraform:

```bash
terraform init
terraform plan
terraform apply
```

## Notes

* Only port `80` is exposed publicly.
* SSH is restricted by `admin_cidr_block`.
* `terraform.tfvars` is ignored by Git; keep secrets there, not in source files.
