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

## GitHub Actions

The repository also includes a dedicated Terraform workflow:

```text
.github/workflows/terraform.yml
```

It runs `terraform fmt`, `terraform init`, `terraform validate`, and `terraform plan` automatically when Terraform files change.

Applying infrastructure changes is manual through `workflow_dispatch` with the `apply` input enabled.

Required GitHub Secrets:

* `AWS_ACCESS_KEY_ID`: AWS access key used by Terraform
* `AWS_SECRET_ACCESS_KEY`: AWS secret key used by Terraform
* `AWS_REGION`: AWS region, for example `eu-west-3`
* `TF_ADMIN_CIDR_BLOCK`: CIDR allowed to access SSH, for example `203.0.113.10/32`
* `TF_SSH_PUBLIC_KEY`: public SSH key content, for example `ssh-rsa AAAA...`

## Notes

* Only port `80` is exposed publicly.
* SSH is restricted by `admin_cidr_block`.
* `terraform.tfvars` is ignored by Git; keep secrets there, not in source files.
