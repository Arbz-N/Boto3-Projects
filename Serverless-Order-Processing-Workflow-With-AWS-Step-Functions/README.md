Serverless Order Processing Workflow

    Overview
    This project demonstrates a serverless order processing pipeline using AWS Step Functions.
    A JSON file uploaded to S3 triggers a Lambda function which starts a Step Functions execution. 
    The state machine writes the order to DynamoDB then calls a second Lambda to process it.



Architecture:

    S3 Upload (test-order.json)
        |
        | Event Trigger
        v
    Step-Triggering-Lambda
        |
        | start_execution()
        v
    Step Functions State Machine (Lab5-OrderProcessingStateMachine)
        |
        |-- State 1: Add Order Entry --> DynamoDB putItem
        |
        |-- State 2: Process Order   --> Lab5-ProcessOrderFunction (Lambda)


Project Structure:

        Serverless-Order-Processing-Workflow-With-AWS-Step-Functions/
        |
        |-- step_triggering_lambda.py       # S3 event -> Step Functions trigger
        |-- process_order_lambda.py         # Order processing Lambda
        |-- state_machine_definition.json   # Step Functions state machine JSON
        |-- test-order.json                 # Single order test file
        |-- multi-orders.json               # Multiple orders test file
        |
        |-- README.md

Prerequisites

# AWS configured?
aws sts get-caller-identity

# Apni values ready rakho:
# AWS_REGION = your-region
# ACCOUNT_ID = your-12-digit-account-id
aws sts get-caller-identity --query 'Account' --output text

Task 1 — Create S3 Bucket
bashaws s3 mb s3://lab5-order-json-bucket --region your-region

Task 2 — Create IAM Role
AWS Console → IAM → Roles → Create role

Trusted entity: Lambda
Role name:      Lambda-Role

Attach the following policies:
  - AmazonS3FullAccess
  - AmazonDynamoDBFullAccess
  - AWSLambdaBasicExecutionRole
  - AWSStepFunctionFullAccess

Task 3 — Create DynamoDB Table
AWS Console → DynamoDB → Create table

Table Name:    Lab5-CustomerOrdersTable
Partition Key: customerId  (String)
Sort Key:      orderId     (String)
The combination of customerId and orderId forms the composite primary key. Both fields are required to uniquely identify an item.

Task 4 — Deploy Lambda Functions
Step-Triggering-Lambda
AWS Console → Lambda → Create function
  Name:    Step-Triggering-Lambda
  Runtime: Python 3.x
  Role:    Lambda-Role
  Timeout: 1 minute (increase from default 3 seconds)
Paste the code from step_triggering_lambda.py and update the CONFIG section:
pythonREGION     = "your-region"
ACCOUNT_ID = "your-account-id"
Lab5-ProcessOrderFunction
AWS Console → Lambda → Create function
  Name:    Lab5-ProcessOrderFunction
  Runtime: Python 3.x
  Role:    Lambda-Role
Paste the code from process_order_lambda.py.

Task 5 — Configure S3 Event Trigger
AWS Console → S3 → lab5-order-json-bucket
  → Properties → Event notifications → Create event notification

  Name:        S3Trigger
  Event type:  All object create events
  Destination: Lambda function → Step-Triggering-Lambda

Task 6 — Create State Machine
AWS Console → Step Functions → Create state machine
  → Write your workflow in code
Paste the content from state_machine_definition.json and replace the Lambda ARN placeholder:
json"Resource": "arn:aws:lambda:YOUR-REGION:YOUR-ACCOUNT-ID:function:Lab5-ProcessOrderFunction"
State Machine name: Lab5-OrderProcessingStateMachine
Type:               Standard

Task 7 — Update State Machine ARN in Lambda
After creating the state machine, copy its ARN from the console and update the CONFIG in step_triggering_lambda.py:
pythonREGION     = "your-actual-region"
ACCOUNT_ID = "your-actual-account-id"

Task 8 — Test with Single Order
bash# Upload the test file to trigger the workflow
aws s3 cp test-order.json s3://lab5-order-json-bucket/

# Verify execution in Step Functions Console
# Step Functions → Lab5-OrderProcessingStateMachine → Executions

# Verify item in DynamoDB
aws dynamodb get-item \
  --table-name Lab5-CustomerOrdersTable \
  --key '{"customerId": {"S": "972"}, "orderId": {"S": "oId-100"}}' \
  --region your-region

Task 9 — Test with Multiple Orders
bash# Upload multiple orders file
aws s3 cp multi-orders.json s3://lab5-order-json-bucket/
Three separate Step Functions executions will start. Each order will be written to DynamoDB and processed by the Lambda function independently.

Cleanup
bash# S3
aws s3 rm s3://lab5-order-json-bucket --recursive
aws s3 rb s3://lab5-order-json-bucket

# DynamoDB
aws dynamodb delete-table \
  --table-name Lab5-CustomerOrdersTable \
  --region your-region

# Lambda
aws lambda delete-function --function-name Step-Triggering-Lambda
aws lambda delete-function --function-name Lab5-ProcessOrderFunction

# Step Functions
aws stepfunctions delete-state-machine \
  --state-machine-arn arn:aws:states:YOUR-REGION:YOUR-ACCOUNT-ID:stateMachine:Lab5-OrderProcessingStateMachine

# IAM Role
aws iam detach-role-policy --role-name Lambda-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-role-policy --role-name Lambda-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-role-policy --role-name Lambda-Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name Lambda-Role

License
MIT License