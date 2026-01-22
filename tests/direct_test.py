import boto3
import json
import uuid
from botocore.exceptions import ClientError

# Configure boto3 to use LocalStack
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

table_name = 'dev-serverless-api-items-table'
table = dynamodb.Table(table_name)

def test_create_item():
    """Test creating an item in DynamoDB"""
    print("Testing CREATE item functionality...")
    
    # Create a test item
    item_id = str(uuid.uuid4())
    item = {
        'itemId': item_id,
        'name': 'Direct Test Item',
        'description': 'Created via direct DynamoDB test',
        'category': 'test'
    }
    
    try:
        # Put item in DynamoDB
        response = table.put_item(Item=item)
        print(f"✓ Successfully created item with ID: {item_id}")
        print(f"Response: {response}")
        return item_id
    except ClientError as e:
        print(f"✗ Failed to create item: {e}")
        return None

def test_get_item(item_id):
    """Test retrieving an item from DynamoDB"""
    print(f"\nTesting GET item functionality for ID: {item_id}...")
    
    try:
        # Get item from DynamoDB
        response = table.get_item(Key={'itemId': item_id})
        
        if 'Item' in response:
            item = response['Item']
            print(f"✓ Successfully retrieved item:")
            print(f"  ID: {item['itemId']}")
            print(f"  Name: {item['name']}")
            print(f"  Description: {item['description']}")
            return True
        else:
            print(f"✗ Item not found")
            return False
    except ClientError as e:
        print(f"✗ Failed to retrieve item: {e}")
        return False

def test_get_nonexistent_item():
    """Test retrieving a non-existent item"""
    print(f"\nTesting GET nonexistent item functionality...")
    
    fake_id = str(uuid.uuid4())
    try:
        response = table.get_item(Key={'itemId': fake_id})
        
        if 'Item' not in response:
            print(f"✓ Correctly returned empty for non-existent item")
            return True
        else:
            print(f"✗ Should have returned empty for non-existent item")
            return False
    except ClientError as e:
        print(f"✗ Error retrieving non-existent item: {e}")
        return False

if __name__ == "__main__":
    print("Running Direct DynamoDB Tests Against LocalStack")
    print("=" * 50)
    
    # Test create item
    created_item_id = test_create_item()
    
    if created_item_id:
        # Test get item
        get_success = test_get_item(created_item_id)
        
        # Test get non-existent item
        nonexistent_success = test_get_nonexistent_item()
        
        if get_success and nonexistent_success:
            print("\n🎉 All direct DynamoDB tests passed!")
        else:
            print("\n❌ Some direct tests failed.")
    else:
        print("\n❌ Could not create test item, skipping other tests.")