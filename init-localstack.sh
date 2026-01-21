#!/bin/bash

echo "Initializing LocalStack resources..."

# Wait for LocalStack to be ready
sleep 10

# Create DynamoDB table
awslocal dynamodb create-table \
    --table-name dev-serverless-api-items-table \
    --attribute-definitions AttributeName=itemId,AttributeType=S \
    --key-schema AttributeName=itemId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url=http://localhost:4566

echo "DynamoDB table created"

# Verify resources
awslocal dynamodb list-tables --endpoint-url=http://localhost:4566

echo "LocalStack initialization completed"