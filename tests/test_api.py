import requests
import json
import time
import uuid
import random

def test_api_endpoints(api_base_url):
    """
    Integration tests for the serverless API
    """
    print("Starting API integration tests...")
    
    # Test POST /items - Create an item
    print("\n1. Testing POST /items endpoint")
    item_data = {
        "name": f"Test Item {random.randint(1000, 9999)}",
        "description": "This is a test item created by integration tests",
        "category": "test",
        "price": 29.99
    }
    
    try:
        response = requests.post(f"{api_base_url}/items", json=item_data)
        print(f"POST /items Status Code: {response.status_code}")
        print(f"POST /items Response: {response.text}")
        
        if response.status_code == 201:
            response_data = response.json()
            item_id = response_data.get('itemId')
            print(f"✓ Successfully created item with ID: {item_id}")
        else:
            print(f"✗ Failed to create item. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during POST /items: {str(e)}")
        return False
    
    # Wait a moment for the item to be stored
    time.sleep(1)
    
    # Test GET /items/{id} - Retrieve the created item
    print(f"\n2. Testing GET /items/{item_id} endpoint")
    try:
        response = requests.get(f"{api_base_url}/items/{item_id}")
        print(f"GET /items/{item_id} Status Code: {response.status_code}")
        print(f"GET /items/{item_id} Response: {response.text}")
        
        if response.status_code == 200:
            item_details = response.json()
            if item_details.get('itemId') == item_id:
                print(f"✓ Successfully retrieved item with ID: {item_id}")
            else:
                print(f"✗ Retrieved item ID doesn't match. Expected: {item_id}, Got: {item_details.get('itemId')}")
                return False
        else:
            print(f"✗ Failed to retrieve item. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during GET /items/{item_id}: {str(e)}")
        return False
    
    # Test GET /items/{nonexistent_id} - Try to retrieve a non-existent item
    print(f"\n3. Testing GET /items/{str(uuid.uuid4())} endpoint (should return 404)")
    fake_id = str(uuid.uuid4())
    try:
        response = requests.get(f"{api_base_url}/items/{fake_id}")
        print(f"GET /items/{fake_id} Status Code: {response.status_code}")
        print(f"GET /items/{fake_id} Response: {response.text}")
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent item")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during GET /items/{fake_id}: {str(e)}")
        return False
    
    # Test POST /items with missing required field - Should return 400
    print(f"\n4. Testing POST /items with missing required field (should return 400)")
    invalid_item_data = {
        "description": "This item is missing the required 'name' field"
    }
    
    try:
        response = requests.post(f"{api_base_url}/items", json=invalid_item_data)
        print(f"POST /items (invalid) Status Code: {response.status_code}")
        print(f"POST /items (invalid) Response: {response.text}")
        
        if response.status_code == 400:
            print("✓ Correctly returned 400 for invalid input")
        else:
            print(f"✗ Expected 400, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during POST /items (invalid): {str(e)}")
        return False
    
    # Test PUT /items/{id} - Update the created item
    print(f"\n5. Testing PUT /items/{item_id} endpoint")
    updated_item_data = {
        "name": f"Updated Test Item {random.randint(10000, 99999)}",
        "description": "This is an updated test item",
        "category": "updated-test",
        "price": 39.99
    }
    
    try:
        response = requests.put(f"{api_base_url}/items/{item_id}", json=updated_item_data)
        print(f"PUT /items/{item_id} Status Code: {response.status_code}")
        print(f"PUT /items/{item_id} Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('itemId') == item_id:
                print(f"✓ Successfully updated item with ID: {item_id}")
            else:
                print(f"✗ Updated item ID doesn't match. Expected: {item_id}, Got: {response_data.get('itemId')}")
                return False
        else:
            print(f"✗ Failed to update item. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during PUT /items/{item_id}: {str(e)}")
        return False
    
    # Test PUT /items/{nonexistent_id} - Try to update a non-existent item
    print(f"\n6. Testing PUT /items/{fake_id} endpoint (should return 404)")
    try:
        response = requests.put(f"{api_base_url}/items/{fake_id}", json=updated_item_data)
        print(f"PUT /items/{fake_id} Status Code: {response.status_code}")
        print(f"PUT /items/{fake_id} Response: {response.text}")
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent item update")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during PUT /items/{fake_id}: {str(e)}")
        return False
    
    # Test DELETE /items/{id} - Delete the created item
    print(f"\n7. Testing DELETE /items/{item_id} endpoint")
    
    try:
        response = requests.delete(f"{api_base_url}/items/{item_id}")
        print(f"DELETE /items/{item_id} Status Code: {response.status_code}")
        print(f"DELETE /items/{item_id} Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('itemId') == item_id:
                print(f"✓ Successfully deleted item with ID: {item_id}")
            else:
                print(f"✗ Deleted item ID doesn't match. Expected: {item_id}, Got: {response_data.get('itemId')}")
                return False
        else:
            print(f"✗ Failed to delete item. Status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during DELETE /items/{item_id}: {str(e)}")
        return False
    
    # Test DELETE /items/{nonexistent_id} - Try to delete a non-existent item
    print(f"\n8. Testing DELETE /items/{fake_id} endpoint (should return 404)")
    try:
        response = requests.delete(f"{api_base_url}/items/{fake_id}")
        print(f"DELETE /items/{fake_id} Status Code: {response.status_code}")
        print(f"DELETE /items/{fake_id} Response: {response.text}")
        
        if response.status_code == 404:
            print("✓ Correctly returned 404 for non-existent item deletion")
        else:
            print(f"✗ Expected 404, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during DELETE /items/{fake_id}: {str(e)}")
        return False
    
    print("\n✓ All integration tests passed!")
    return True

if __name__ == "__main__":
    # The API base URL should be passed as an environment variable or command line argument
    # For now, we'll use a placeholder - this will be replaced during actual testing
    import os
    api_url = os.getenv("API_BASE_URL", "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1")
    
    print(f"Testing API at: {api_url}")
    success = test_api_endpoints(api_url)
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed.")
        exit(1)