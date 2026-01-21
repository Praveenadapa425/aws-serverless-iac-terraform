output "api_gateway_url" {
  description = "API Gateway base URL"
  value       = "${var.region}.amazonaws.com/${aws_api_gateway_stage.api_gateway_stage.stage_name}/${aws_api_gateway_rest_api.serverless_api.name}"
}

output "api_gateway_endpoint" {
  description = "Full API Gateway endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.serverless_api.id}.execute-api.${var.region}.amazonaws.com/${var.api_gateway_stage}"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.items_handler.function_name
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  value       = aws_dynamodb_table.items_table.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.items_table.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}

output "iam_role_name" {
  description = "Name of the IAM role for Lambda"
  value       = aws_iam_role.lambda_role.name
}

output "items_post_endpoint" {
  description = "POST /items endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.serverless_api.id}.execute-api.${var.region}.amazonaws.com/${var.api_gateway_stage}/items"
}

output "items_get_endpoint" {
  description = "GET /items/{id} endpoint URL"
  value       = "https://${aws_api_gateway_rest_api.serverless_api.id}.execute-api.${var.region}.amazonaws.com/${var.api_gateway_stage}/items/{id}"
}