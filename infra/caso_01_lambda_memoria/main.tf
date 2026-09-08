provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
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
