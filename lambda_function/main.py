import json
import boto3
import uuid
import os
import time
import logging
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', '')
table = dynamodb.Table(table_name)

def handler(event, context):
    """
    Main Lambda handler for API Gateway requests
    """
    # Extract request details
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_parameters = event.get('pathParameters', {}) or {}
    body = event.get('body', '')
    
    # Parse request body if it's a string
    if body and isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
    
    request_id = context.aws_request_id
    
    # Log incoming request
    log_event = {
        'message': 'Incoming request',
        'requestId': request_id,
        'httpMethod': http_method,
        'path': path,
        'timestamp': datetime.utcnow().isoformat()
    }
    logger.info(log_event)
    
    try:
        # Route based on HTTP method and path
        if http_method == 'POST' and path.endswith('/items'):
            response = handle_create_item(body, request_id)
        elif http_method == 'GET' and '/items/' in path:
            item_id = path_parameters.get('id') or path.split('/')[-1]
            response = handle_get_item(item_id, request_id)
        elif http_method == 'PUT' and '/items/' in path:
            item_id = path_parameters.get('id') or path.split('/')[-1]
            response = handle_update_item(item_id, body, request_id)
        elif http_method == 'DELETE' and '/items/' in path:
            item_id = path_parameters.get('id') or path.split('/')[-1]
            response = handle_delete_item(item_id, request_id)
        else:
            # Unsupported route
            error_msg = f'Unsupported route: {http_method} {path}'
            logger.warning({'message': error_msg, 'requestId': request_id})
            response = {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Not found'})
            }
        
        # Add successful operation log
        log_event = {
            'message': 'Request processed successfully',
            'requestId': request_id,
            'statusCode': response['statusCode'],
            'path': path,
            'httpMethod': http_method,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(log_event)
        
        # Publish custom metrics
        try:
            publish_custom_metrics(context.function_name, 'SuccessfulInvocations', 1)
        except:
            # Continue even if metrics publishing fails
            pass
        
        return response
        
    except Exception as e:
        # Log error
        error_log = {
            'message': 'Error processing request',
            'requestId': request_id,
            'error': str(e),
            'path': path,
            'httpMethod': http_method,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.error(error_log)
        
        # Publish error metric
        try:
            publish_custom_metrics(context.function_name, 'InvocationErrors', 1)
        except:
            # Continue even if metrics publishing fails
            pass
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_create_item(body, request_id):
    """
    Handle POST /items to create a new item
    """
    # Validate input
    if not body or not isinstance(body, dict):
        validation_error = {
            'message': 'Invalid input: body must be a JSON object',
            'requestId': request_id
        }
        logger.warning(validation_error)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid input: body must be a JSON object'})
        }
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in body:
            validation_error = {
                'message': f'Missing required field: {field}',
                'requestId': request_id
            }
            logger.warning(validation_error)
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }
    
    # Generate a unique ID for the item
    item_id = str(uuid.uuid4())
    
    # Prepare item for DynamoDB
    timestamp = int(time.time())
    item = {
        'itemId': item_id,
        'name': body['name'],
        'description': body.get('description', ''),
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    
    # Add any additional fields from the request
    for key, value in body.items():
        if key not in ['name', 'description']:
            item[key] = value
    
    try:
        # Put item in DynamoDB
        table.put_item(Item=item)
        
        # Log successful creation
        success_log = {
            'message': 'Item created successfully',
            'requestId': request_id,
            'itemId': item_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(success_log)
        
        # Calculate processing time (simulate)
        start_time = time.time()
        time.sleep(0.01)  # Simulated processing
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Publish processing time metric
        try:
            publish_custom_metrics(context.function_name, 'ProcessingTime', processing_time)
        except:
            # Continue even if metrics publishing fails
            pass
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'itemId': item_id,
                'message': 'Item created successfully'
            })
        }
    except ClientError as e:
        error_log = {
            'message': 'Failed to create item in DynamoDB',
            'requestId': request_id,
            'error': str(e),
            'itemId': item_id
        }
        logger.error(error_log)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to create item'})
        }

def handle_get_item(item_id, request_id):
    """
    Handle GET /items/{id} to retrieve an item
    """
    if not item_id:
        validation_error = {
            'message': 'Item ID is required',
            'requestId': request_id
        }
        logger.warning(validation_error)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Item ID is required'})
        }
    
    try:
        # Get item from DynamoDB
        response = table.get_item(Key={'itemId': item_id})
        
        if 'Item' not in response:
            # Item not found
            not_found_log = {
                'message': 'Item not found',
                'requestId': request_id,
                'itemId': item_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.info(not_found_log)
            
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Item not found'})
            }
        
        # Log successful retrieval
        success_log = {
            'message': 'Item retrieved successfully',
            'requestId': request_id,
            'itemId': item_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(success_log)
        
        # Return the item
        item = response['Item']
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(item, default=str)  # Convert datetime objects to string
        }
    except ClientError as e:
        error_log = {
            'message': 'Failed to retrieve item from DynamoDB',
            'requestId': request_id,
            'error': str(e),
            'itemId': item_id
        }
        logger.error(error_log)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to retrieve item'})
        }

def handle_update_item(item_id, body, request_id):
    """
    Handle PUT /items/{id} to update an item
    """
    if not item_id:
        validation_error = {
            'message': 'Item ID is required for update',
            'requestId': request_id
        }
        logger.warning(validation_error)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Item ID is required for update'})
        }
    
    if not body or not isinstance(body, dict):
        validation_error = {
            'message': 'Invalid input: body must be a JSON object',
            'requestId': request_id
        }
        logger.warning(validation_error)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Invalid input: body must be a JSON object'})
        }
    
    try:
        # Check if item exists
        existing_item = table.get_item(Key={'itemId': item_id})
        
        if 'Item' not in existing_item:
            not_found_log = {
                'message': 'Item not found for update',
                'requestId': request_id,
                'itemId': item_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.info(not_found_log)
            
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Item not found'})
            }
        
        # Prepare update expression
        update_expression = "SET updatedAt = :updated_at"
        expression_values = {':updated_at': int(time.time())}
        
        # Add fields to update
        for key, value in body.items():
            if key not in ['itemId', 'createdAt']:  # Don't allow updating these fields
                update_expression += f", {key} = :{key}"
                expression_values[f':{key}'] = value
        
        # Update item in DynamoDB
        table.update_item(
            Key={'itemId': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        
        # Log successful update
        success_log = {
            'message': 'Item updated successfully',
            'requestId': request_id,
            'itemId': item_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(success_log)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'itemId': item_id,
                'message': 'Item updated successfully'
            })
        }
    except ClientError as e:
        error_log = {
            'message': 'Failed to update item in DynamoDB',
            'requestId': request_id,
            'error': str(e),
            'itemId': item_id
        }
        logger.error(error_log)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to update item'})
        }

def handle_delete_item(item_id, request_id):
    """
    Handle DELETE /items/{id} to delete an item
    """
    if not item_id:
        validation_error = {
            'message': 'Item ID is required for deletion',
            'requestId': request_id
        }
        logger.warning(validation_error)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Item ID is required for deletion'})
        }
    
    try:
        # Check if item exists
        existing_item = table.get_item(Key={'itemId': item_id})
        
        if 'Item' not in existing_item:
            not_found_log = {
                'message': 'Item not found for deletion',
                'requestId': request_id,
                'itemId': item_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            logger.info(not_found_log)
            
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Item not found'})
            }
        
        # Delete item from DynamoDB
        table.delete_item(Key={'itemId': item_id})
        
        # Log successful deletion
        success_log = {
            'message': 'Item deleted successfully',
            'requestId': request_id,
            'itemId': item_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        logger.info(success_log)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'itemId': item_id,
                'message': 'Item deleted successfully'
            })
        }
    except ClientError as e:
        error_log = {
            'message': 'Failed to delete item from DynamoDB',
            'requestId': request_id,
            'error': str(e),
            'itemId': item_id
        }
        logger.error(error_log)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to delete item'})
        }

def publish_custom_metrics(function_name, metric_name, value):
    """
    Publish custom metrics to CloudWatch
    """
    try:
        cloudwatch = boto3.client('cloudwatch')
        
        cloudwatch.put_metric_data(
            Namespace='ServerlessAPI/Custom',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': 'Count' if metric_name != 'ProcessingTime' else 'Milliseconds',
                    'Dimensions': [
                        {
                            'Name': 'FunctionName',
                            'Value': function_name
                        }
                    ]
                }
            ]
        )
    except Exception as e:
        # Don't fail the function if metrics publishing fails
        logger.warning({
            'message': 'Failed to publish custom metric',
            'metricName': metric_name,
            'error': str(e)
        })