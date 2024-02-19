#!/bin/bash

# List of Terraform configuration files to check for changes
CONFIG_FILES=("main.tf" "variables.tf" "dev-backend.tf" "dev.tfvars" "prod.tfvars")

# A function that checks if any of the specified files have changed
any_files_changed() {
  for file in "${CONFIG_FILES[@]}"; do
    git diff --quiet HEAD "${file}"
    if [ $? -ne 0 ]; then
      return 0
    fi
  done
  return 1
}

# Run Terraform if any of the specified configuration files have changed
if any_files_changed; then
  echo "Changes detected, running Terraform..."
  terraform --version
  terraform init --backend-config=dev-backend.tfvars
  terraform plan -var-file=dev.tfvars
  terraform apply -var-file=dev.tfvars --auto-approve
  echo "stack has been created or updated properly"
else
  echo "No changes detected, skipping Terraform run."
fi
