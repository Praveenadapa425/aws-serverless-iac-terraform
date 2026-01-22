# AWS Serverless API with Terraform

This project demonstrates a production-ready serverless API built on AWS using Infrastructure as Code (IaC) with Terraform. The architecture includes API Gateway, Lambda functions, DynamoDB, and comprehensive monitoring with CloudWatch.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│   Lambda Func   │───▶│   DynamoDB      │
│                 │    │                 │    │                 │
│  /items (POST)  │    │  Python Handler │    │  Items Table    │
│  /items/{id}(GET)│    │                 │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  CloudWatch     │    │  CloudWatch      │    │  CloudWatch     │
│  API Metrics    │    │  Logs            │    │  Alarms         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components:
- **API Gateway**: REST API with four endpoints (POST /items, GET /items/{id}, PUT /items/{id}, DELETE /items/{id})
- **Lambda Function**: Python-based business logic for CRUD operations
- **DynamoDB**: NoSQL database for storing items
- **CloudWatch**: Logging, metrics, and alarms for observability
- **IAM**: Least-privilege roles and policies

## 🚀 Prerequisites

- AWS CLI installed and configured
- Terraform v1.0+ installed
- Docker and Docker Compose (for local development)
- Python 3.9+ (for local development)

## 📁 Project Structure

```
.
├── main.tf                 # Main Terraform configuration
├── variables.tf            # Input variables for Terraform
├── outputs.tf              # Output values from deployment
├── versions.tf             # Terraform and provider version constraints
├── modules/
│   ├── lambda/             # Lambda function module
│   └── dynamodb/           # DynamoDB table module
├── lambda_function/
│   ├── main.py             # Lambda handler code
│   └── requirements.txt    # Python dependencies
├── tests/
│   └── test_api.py         # Integration tests
├── docker-compose.yml      # LocalStack configuration
├── init-localstack.sh      # LocalStack initialization script
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
└── README.md               # Project documentation
```

## ⚙️ Setup and Configuration

### 1. Environment Setup

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Update the `.env` file with your AWS credentials and configuration values.

### 2. Remote State Configuration

This project uses remote state management. Before deploying, you'll need to:

1. Create an S3 bucket for state storage
2. Create a DynamoDB table for state locking
3. Update `main.tf` with your bucket and table names

### 3. Install Dependencies

```bash
# Install Python dependencies for Lambda
cd lambda_function
pip install -r requirements.txt -t .
cd ..

# Zip the Lambda function
cd lambda_function
zip -r main.zip .
cd ..
```

## 🚀 Deployment

### 1. Initialize Terraform

```bash
terraform init
```

### 2. Review the Plan

```bash
terraform plan
```

### 3. Apply the Configuration

```bash
terraform apply
```

### 4. View Outputs

After deployment, view the outputs to get your API endpoint:

```bash
terraform output
```

## 🔧 API Endpoints

### POST /items
Create a new item.

**Request Body:**
```json
{
  "name": "Sample Item",
  "description": "This is a sample item",
  "category": "electronics",
  "price": 99.99
}
```

**Response:**
```json
{
  "itemId": "uuid-string",
  "message": "Item created successfully"
}
```

**Status Codes:**
- `201 Created`: Item created successfully
- `400 Bad Request`: Invalid input data

### GET /items/{id}
Retrieve an item by ID.

**Response:**
```json
{
  "itemId": "uuid-string",
  "name": "Sample Item",
  "description": "This is a sample item",
  "category": "electronics",
  "price": 99.99,
  "createdAt": 1234567890,
  "updatedAt": 1234567890
}
```

**Status Codes:**
- `200 OK`: Item found and returned
- `404 Not Found`: Item does not exist

### PUT /items/{id}
Update an existing item.

**Request Body:**
```json
{
  "name": "Updated Sample Item",
  "description": "This is an updated sample item",
  "category": "electronics",
  "price": 149.99
}
```

**Response:**
```json
{
  "itemId": "uuid-string",
  "message": "Item updated successfully"
}
```

**Success Response Example:**
```json
{
  "itemId": "abc123-4567-8901-def2",
  "message": "Item updated successfully"
}
```

**Error Response Example (404):**
```json
{
  "error": "Item not found"
}
```

**Status Codes:**
- `200 OK`: Item updated successfully
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Item does not exist

### DELETE /items/{id}
Delete an item by ID.

**Response:**
```json
{
  "itemId": "uuid-string",
  "message": "Item deleted successfully"
}
```

**Success Response Example:**
```json
{
  "itemId": "abc123-4567-8901-def2",
  "message": "Item deleted successfully"
}
```

**Error Response Example (404):**
```json
{
  "error": "Item not found"
}
```

**Status Codes:**
- `200 OK`: Item deleted successfully
- `400 Bad Request`: Invalid item ID
- `404 Not Found`: Item does not exist

## 📊 Monitoring and Observability

### CloudWatch Metrics
The following custom metrics are published:
- `ServerlessAPI/Custom/SuccessfulInvocations`: Count of successful API invocations
- `ServerlessAPI/Custom/InvocationErrors`: Count of invocation errors
- `ServerlessAPI/Custom/ProcessingTime`: Processing time in milliseconds

### CloudWatch Alarms
- **Lambda Error Alarm**: Triggers when InvocationErrors >= 5 in 5 minutes
- **Lambda Duration Alarm**: Triggers when average ProcessingTime > 5 seconds

### CloudWatch Alarms
- **Lambda Error Alarm**: Triggers when error count >= 5 in 5 minutes
- **Lambda Duration Alarm**: Triggers when average duration > 5 seconds

### Structured Logging
All Lambda functions output structured JSON logs including:
- Request ID
- HTTP method and path
- Timestamp
- Processing status
- Error details (if any)

## 🧪 Testing

### Integration Tests
Run integration tests against your deployed API:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Set the API base URL
export API_BASE_URL=$(terraform output -raw api_gateway_endpoint)

# Run tests
python tests/test_api.py
```

### Local Development with LocalStack
Start LocalStack for local development:

```bash
# Start LocalStack
docker-compose up -d

# Run direct DynamoDB tests (bypassing Lambda networking issues)
python tests/direct_test.py
```

## 🛡️ Security Best Practices

- **Least Privilege IAM**: Lambda function has minimal required permissions
- **Input Validation**: All API inputs are validated before processing
- **Secure Logging**: No sensitive data is logged
- **Resource Tagging**: All resources are tagged for cost tracking

## 🗂️ Terraform Modules

### Lambda Module
- Creates Lambda function with proper IAM role
- Sets up CloudWatch log group
- Configures environment variables

### DynamoDB Module
- Creates DynamoDB table with provisioned throughput
- Defines primary key schema
- Applies resource tags

## 🛠️ Maintenance

### Updating Infrastructure
1. Modify Terraform configuration files
2. Run `terraform plan` to review changes
3. Run `terraform apply` to deploy changes

### Destroying Infrastructure
To tear down all resources:

```bash
terraform destroy
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

Made with ❤️ using AWS, Terraform, and Python