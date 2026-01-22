import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda_function'))

# Mock the AWS services
import json
from unittest.mock import Mock, patch

def test_lambda_handler_logic():
    """Test the core logic of the Lambda handler without AWS dependencies"""
    
    # Import the main module
    import main
    
    # Mock the DynamoDB table
    mock_table = Mock()
    main.table = mock_table
    
    # Mock the CloudWatch client
    mock_cloudwatch = Mock()
    with patch('boto3.client', return_value=mock_cloudwatch):
        
        # Test 1: POST /items - Valid request
        print("Testing POST /items with valid data...")
        event = {
            'httpMethod': 'POST',
            'path': '/items',
            'body': '{"name": "Test Item", "description": "Test Description"}'
        }
        
        # Mock successful DynamoDB put_item
        mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        response = main.handler(event, Mock(aws_request_id='test-request-123'))
        
        assert response['statusCode'] == 201
        assert 'itemId' in json.loads(response['body'])
        print("✓ POST /items test passed")
        
        # Test 2: GET /items/{id} - Item found
        print("Testing GET /items/{id} with existing item...")
        event = {
            'httpMethod': 'GET',
            'path': '/items/test-item-id',
            'pathParameters': {'id': 'test-item-id'}
        }
        
        # Mock successful DynamoDB get_item
        mock_table.get_item.return_value = {
            'Item': {
                'itemId': 'test-item-id',
                'name': 'Test Item',
                'description': 'Test Description'
            }
        }
        
        response = main.handler(event, Mock(aws_request_id='test-request-456'))
        
        assert response['statusCode'] == 200
        item = json.loads(response['body'])
        assert item['itemId'] == 'test-item-id'
        print("✓ GET /items/{id} test passed")
        
        # Test 3: GET /items/{id} - Item not found
        print("Testing GET /items/{id} with non-existent item...")
        mock_table.get_item.return_value = {}
        
        response = main.handler(event, Mock(aws_request_id='test-request-789'))
        
        assert response['statusCode'] == 404
        print("✓ GET /items/{id} not found test passed")
        
        # Test 4: PUT /items/{id} - Valid update
        print("Testing PUT /items/{id} with valid data...")
        event = {
            'httpMethod': 'PUT',
            'path': '/items/test-item-id',
            'pathParameters': {'id': 'test-item-id'},
            'body': '{"name": "Updated Test Item", "description": "Updated Description"}'
        }
        
        # Mock item exists for update
        mock_table.get_item.return_value = {
            'Item': {'itemId': 'test-item-id', 'name': 'Old Name'}
        }
        mock_table.update_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        response = main.handler(event, Mock(aws_request_id='test-request-101'))
        
        assert response['statusCode'] == 200
        print("✓ PUT /items/{id} test passed")
        
        # Test 5: DELETE /items/{id} - Valid deletion
        print("Testing DELETE /items/{id} with existing item...")
        event = {
            'httpMethod': 'DELETE',
            'path': '/items/test-item-id',
            'pathParameters': {'id': 'test-item-id'}
        }
        
        # Mock item exists for deletion
        mock_table.get_item.return_value = {
            'Item': {'itemId': 'test-item-id'}
        }
        mock_table.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        response = main.handler(event, Mock(aws_request_id='test-request-102'))
        
        assert response['statusCode'] == 200
        print("✓ DELETE /items/{id} test passed")
        
        # Test 6: Input validation - Missing required field
        print("Testing POST /items with missing required field...")
        event = {
            'httpMethod': 'POST',
            'path': '/items',
            'body': '{"description": "Missing name field"}'
        }
        
        response = main.handler(event, Mock(aws_request_id='test-request-103'))
        
        assert response['statusCode'] == 400
        print("✓ Input validation test passed")
        
        print("\n🎉 All Lambda logic tests passed!")

if __name__ == "__main__":
    test_lambda_handler_logic()