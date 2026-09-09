provider "aws" {
  region  = var.aws_region
  profile = var.use_localstack ? null : var.aws_profile

  # Credenciales dummy y endpoints redirigidos al gemelo digital (LocalStack),
  # el mismo mecanismo que usará `shadowstack apply` para simular cambios
  # sin tocar AWS real.
  access_key                  = var.use_localstack ? "test" : null
  secret_key                  = var.use_localstack ? "test" : null
  skip_credentials_validation = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  skip_requesting_account_id  = var.use_localstack

  endpoints {
    lambda     = var.use_localstack ? "http://localhost:4566" : null
    iam        = var.use_localstack ? "http://localhost:4566" : null
    sts        = var.use_localstack ? "http://localhost:4566" : null
    cloudwatch = var.use_localstack ? "http://localhost:4566" : null
    logs       = var.use_localstack ? "http://localhost:4566" : null
    apigateway = var.use_localstack ? "http://localhost:4566" : null
    dynamodb   = var.use_localstack ? "http://localhost:4566" : null
  }
}

data "archive_file" "lambda_source" {
  type        = "zip"
  source_file = "${path.module}/src/handler.py"
  output_path = "${path.module}/build/handler.zip"
}

resource "aws_iam_role" "memoria_exec" {
  name = "${var.function_name}-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "memoria_basic_execution" {
  role       = aws_iam_role.memoria_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "memoria" {
  function_name = var.function_name
  role          = aws_iam_role.memoria_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  memory_size   = var.memory_size
  timeout       = 10

  filename         = data.archive_file.lambda_source.output_path
  source_code_hash = data.archive_file.lambda_source.output_base64sha256
}
