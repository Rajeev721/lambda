provider "aws" {
  region = "us-east-2"
}

terraform {
  backend "s3" {
    encrypt = true
    region = "us-east-2"
  }
}
resource "aws_s3_bucket" "source_bucket" {
  bucket = var.bucket_name
  acl = "private"
  tags = {
        name = "source_bucket"
        environment = var.environment
    }
}

resource "aws_dynamodb_table" "metadata_table"{
    name = var.dynamo_db_table_name
    billing_mode = "PROVISIONED"
    read_capacity = 10
    write_capacity = 10
    hash_key = "id"
    range_key = "start_time"

    attribute {
      name = "id"
      type = "S"
    }
    attribute {
      name = "start_time"
      type = "N"
    }

    ttl {
      attribute_name =  "TimeToExist"
      enabled = false
    }

    tags = {
        name = "metadata-table"
        environment = var.environment
    }

}

resource "aws_lambda_function" "ghactivity_func" {
  function_name = var.lambda_name
  handler       = "lambda_hand.lambda_call"
  runtime       = "python3.10"
  role          = "arn:aws:iam::800832583424:role/service-role/ghactivity-role-6vfr37ay"

  # Replace "path/to/your/lambda.zip" with the actual path to your Lambda deployment package
  filename = "/home/runner/work/lambda/lambda/ghactivity_lambda.zip"

  environment {
    variables = {
      env = var.environment
    }
  }

  tags = {
    resource = "lambda_func"
  }
}

output "s3_bucket_id" {
    value = aws_s3_bucket.source_bucket.id
}

output "s3_bucket_name" {
    value = aws_s3_bucket.source_bucket.bucket
}
output "dynamo_db_table_name" {
    value = aws_dynamodb_table.metadata_table.id
}

output "lambda_name" {
    value = aws_lambda_function.ghactivity_func.function_name
}