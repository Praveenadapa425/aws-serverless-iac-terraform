provider "aws" {
  region = var.region
}

# Configure remote state (you would need to create these resources separately)
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "serverless-api/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "your-terraform-state-lock"
  }
}

# Data source to package the Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function/main.py"
  output_path = "${path.module}/lambda_function/main.zip"
}

# DynamoDB module
module "dynamodb" {
  source = "./modules/dynamodb"
  
  table_name           = "${var.environment}-${var.project_name}-items-table"
  hash_key             = "itemId"
  read_capacity        = var.dynamodb_read_capacity
  write_capacity       = var.dynamodb_write_capacity
  environment          = var.environment
  project_name         = var.project_name
}

# Lambda module
module "lambda" {
  source = "./modules/lambda"
  
  function_name        = "${var.environment}-${var.project_name}-items-handler"
  handler              = "main.handler"
  runtime              = "python3.9"
  filename             = "${path.module}/lambda_function/main.zip"
  timeout              = var.lambda_timeout
  memory_size          = var.lambda_memory_size
  environment          = var.environment
  project_name         = var.project_name
  log_retention_days   = var.log_retention_days
  dynamodb_table_arn   = module.dynamodb.table_arn
  dynamodb_table_name  = module.dynamodb.table_name
}

# API Gateway
resource "aws_api_gateway_rest_api" "serverless_api" {
  name        = "${var.environment}-${var.project_name}-api"
  description = "Serverless API for managing items"
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Resources
resource "aws_api_gateway_resource" "items" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  parent_id   = aws_api_gateway_rest_api.serverless_api.root_resource_id
  path_part   = "items"
}

# Enable CORS for root /items resource
resource "aws_api_gateway_method" "items_options_root" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.items.id
  http_method      = "OPTIONS"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "items_options_root_int" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options_root.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "items_options_root_200" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options_root.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "items_options_root_response" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options_root.http_method
  status_code = aws_api_gateway_method_response.items_options_root_200.status_code

  response_templates = {
    "application/json" = "#set($origin = $input.params("Origin"))
#if($origin == "") #set($origin = $input.params("origin")) #end
{
"principalId": "$context.authorizer.principalId",
"integrationStatus": "200",
"headers": {
"Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
"Access-Control-Allow-Methods": "POST,GET,PUT,DELETE,OPTIONS",
"Access-Control-Allow-Origin": "$origin"
}
}"
  }

  depends_on = [aws_api_gateway_integration.items_options_root_int]
}

resource "aws_api_gateway_resource" "item_by_id" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  parent_id   = aws_api_gateway_resource.items.id
  path_part   = "{id}"
}

# CORS OPTIONS Method for items
resource "aws_api_gateway_method" "items_options" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.items.id
  http_method      = "OPTIONS"
  authorization    = "NONE"
  api_key_required = false
}

resource "aws_api_gateway_integration" "items_options_int" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "items_options_200" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "items_options_response" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_options.http_method
  status_code = aws_api_gateway_method_response.items_options_200.status_code

  response_templates = {
    "application/json" = "#set($origin = $input.params("Origin"))
#if($origin == "") #set($origin = $input.params("origin")) #end
{
"principalId": "$context.authorizer.principalId",
"integrationStatus": "200",
"headers": {
"Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
"Access-Control-Allow-Methods": "POST,GET,PUT,DELETE,OPTIONS",
"Access-Control-Allow-Origin": "$origin"
}
}"
  }

  depends_on = [aws_api_gateway_integration.items_options_int]
}

# Methods
resource "aws_api_gateway_method" "items_post" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.items.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = false

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_method" "item_get" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.item_by_id.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = false

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_method" "item_put" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.item_by_id.id
  http_method      = "PUT"
  authorization    = "NONE"
  api_key_required = false

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_method" "item_delete" {
  rest_api_id      = aws_api_gateway_rest_api.serverless_api.id
  resource_id      = aws_api_gateway_resource.item_by_id.id
  http_method      = "DELETE"
  authorization    = "NONE"
  api_key_required = false

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Integrations
resource "aws_api_gateway_integration" "items_post_int" {
  rest_api_id             = aws_api_gateway_rest_api.serverless_api.id
  resource_id             = aws_api_gateway_resource.items.id
  http_method             = aws_api_gateway_method.items_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambda.invoke_arn
}

resource "aws_api_gateway_integration" "item_get_int" {
  rest_api_id             = aws_api_gateway_rest_api.serverless_api.id
  resource_id             = aws_api_gateway_resource.item_by_id.id
  http_method             = aws_api_gateway_method.item_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambda.invoke_arn
}

resource "aws_api_gateway_integration" "item_put_int" {
  rest_api_id             = aws_api_gateway_rest_api.serverless_api.id
  resource_id             = aws_api_gateway_resource.item_by_id.id
  http_method             = aws_api_gateway_method.item_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambda.invoke_arn
}

resource "aws_api_gateway_integration" "item_delete_int" {
  rest_api_id             = aws_api_gateway_rest_api.serverless_api.id
  resource_id             = aws_api_gateway_resource.item_by_id.id
  http_method             = aws_api_gateway_method.item_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.lambda.invoke_arn
}

# Method responses
resource "aws_api_gateway_method_response" "items_post_ok" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_post.http_method
  status_code = "201"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "items_post_bad_request" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_post.http_method
  status_code = "400"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_get_ok" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_get.http_method
  status_code = "200"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_get_not_found" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_get.http_method
  status_code = "404"
  
  response_models = {
    "application/json" = "Empty"
  }
}

# PUT Method Responses
resource "aws_api_gateway_method_response" "item_put_ok" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = "200"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_put_bad_request" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = "400"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_put_not_found" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = "404"
  
  response_models = {
    "application/json" = "Empty"
  }
}

# DELETE Method Responses
resource "aws_api_gateway_method_response" "item_delete_ok" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = "200"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_delete_bad_request" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = "400"
  
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_method_response" "item_delete_not_found" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = "404"
  
  response_models = {
    "application/json" = "Empty"
  }
}

# Integration responses
resource "aws_api_gateway_integration_response" "items_post_ok_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_post.http_method
  status_code = aws_api_gateway_method_response.items_post_ok.status_code
  
  depends_on = [aws_api_gateway_integration.items_post_int]
}

resource "aws_api_gateway_integration_response" "items_post_bad_request_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.items.id
  http_method = aws_api_gateway_method.items_post.http_method
  status_code = aws_api_gateway_method_response.items_post_bad_request.status_code
  
  depends_on = [aws_api_gateway_integration.items_post_int]
}

resource "aws_api_gateway_integration_response" "item_get_ok_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_get.http_method
  status_code = aws_api_gateway_method_response.item_get_ok.status_code
  
  depends_on = [aws_api_gateway_integration.item_get_int]
}

resource "aws_api_gateway_integration_response" "item_get_not_found_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_get.http_method
  status_code = aws_api_gateway_method_response.item_get_not_found.status_code
  
  depends_on = [aws_api_gateway_integration.item_get_int]
}

# PUT Integration Responses
resource "aws_api_gateway_integration_response" "item_put_ok_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = aws_api_gateway_method_response.item_put_ok.status_code
  
  depends_on = [aws_api_gateway_integration.item_put_int]
}

resource "aws_api_gateway_integration_response" "item_put_bad_request_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = aws_api_gateway_method_response.item_put_bad_request.status_code
  
  depends_on = [aws_api_gateway_integration.item_put_int]
}

resource "aws_api_gateway_integration_response" "item_put_not_found_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_put.http_method
  status_code = aws_api_gateway_method_response.item_put_not_found.status_code
  
  depends_on = [aws_api_gateway_integration.item_put_int]
}

# DELETE Integration Responses
resource "aws_api_gateway_integration_response" "item_delete_ok_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = aws_api_gateway_method_response.item_delete_ok.status_code
  
  depends_on = [aws_api_gateway_integration.item_delete_int]
}

resource "aws_api_gateway_integration_response" "item_delete_bad_request_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = aws_api_gateway_method_response.item_delete_bad_request.status_code
  
  depends_on = [aws_api_gateway_integration.item_delete_int]
}

resource "aws_api_gateway_integration_response" "item_delete_not_found_resp" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  resource_id = aws_api_gateway_resource.item_by_id.id
  http_method = aws_api_gateway_method.item_delete.http_method
  status_code = aws_api_gateway_method_response.item_delete_not_found.status_code
  
  depends_on = [aws_api_gateway_integration.item_delete_int]
}

# Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.serverless_api.id
  stage_name  = var.api_gateway_stage
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_integration.items_post_int,
      aws_api_gateway_integration.item_get_int,
      aws_api_gateway_integration.item_put_int,
      aws_api_gateway_integration.item_delete_int,
      aws_api_gateway_integration.items_options_int,
      aws_api_gateway_integration.items_options_root_int,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Stage
resource "aws_api_gateway_stage" "api_gateway_stage" {
  stage_name    = var.api_gateway_stage
  rest_api_id   = aws_api_gateway_rest_api.serverless_api.id
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  
  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "arn:aws:execute-api:${var.region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.serverless_api.id}/*/*/*"
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_error_alarm" {
  alarm_name          = "${var.environment}-${var.project_name}-lambda-error-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "InvocationErrors"
  namespace           = "ServerlessAPI/Custom"
  period              = var.alarm_period
  statistic           = "Sum"
  threshold           = var.alarm_threshold_errors
  alarm_description   = "This alarm monitors Lambda invocation errors"
  alarm_actions       = []
  
  dimensions = {
    FunctionName = module.lambda.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_duration_alarm" {
  alarm_name          = "${var.environment}-${var.project_name}-lambda-duration-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = var.alarm_evaluation_periods
  metric_name         = "ProcessingTime"
  namespace           = "ServerlessAPI/Custom"
  period              = var.alarm_period
  statistic           = "Average"
  threshold           = 5000  # 5 seconds
  alarm_description   = "This alarm monitors Lambda function duration"
  alarm_actions       = []
  
  dimensions = {
    FunctionName = module.lambda.function_name
  }
}

# Data source for AWS account ID
data "aws_caller_identity" "current" {}