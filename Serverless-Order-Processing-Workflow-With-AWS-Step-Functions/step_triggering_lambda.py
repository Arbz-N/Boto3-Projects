import json
import boto3
import urllib.parse

# ─────────────────────────────────────────────
# CONFIG — update these values before deploying
# ─────────────────────────────────────────────
REGION            = "your-region"        # e.g. us-east-1
ACCOUNT_ID        = "your-account-id"    # 12-digit AWS account ID
STATE_MACHINE_ARN = (
    f"arn:aws:states:{REGION}:{ACCOUNT_ID}"
    ":stateMachine:Lab5-OrderProcessingStateMachine"
)


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    sf_client = boto3.client('stepfunctions')

    # Extract bucket name and file key from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = urllib.parse.unquote_plus(
                 event['Records'][0]['s3']['object']['key'],
                 encoding='utf-8'
             )
    # unquote_plus is required because S3 encodes special characters
    # "my+file.json" becomes "my file.json" after decoding
    # Without decoding: s3.get_object(Key="my+file.json") → FileNotFound

    # Read the file content from S3
    response     = s3_client.get_object(Bucket=bucket, Key=key)
    file_content = response['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    # Handle both single order (dict) and multiple orders (list)
    if isinstance(json_content, dict):
        orders = [json_content]   # wrap single dict in a list
    else:
        orders = json_content     # already a list

    # Start a separate Step Functions execution for each order
    for order in orders:
        sf_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps(order)
            # Step Functions expects a string, not a dict
        )
        print(f"Started execution for orderId: {order.get('orderId')}")

    return {
        'statusCode': 200,
        'body': f"{len(orders)} executions started"
    }