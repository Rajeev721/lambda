variable "environment" {
    description = "This is to define the environment"
    type = string
    default = "dev"
  
}

variable "bucket_name"{
    type = string
    description = "This is source bucket name"
}

variable "dynamo_db_table_name"{
    type = string
    description = "This is dynamo db table name"
}

variable "lambda_name"{
    type = string
    description = "This is lambda name"
}