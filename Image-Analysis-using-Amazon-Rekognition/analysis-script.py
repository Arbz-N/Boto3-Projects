import boto3
from prettytable import PrettyTable
from botocore.exceptions import ClientError

# ─────────────────────────────────────────────
# CONFIG — update these values before running
# ─────────────────────────────────────────────
REGION      = "your-region"
BUCKET_NAME = "your-bucket-name"
TABLE_NAME  = "Rekognition-Labels-Table"

rekognition = boto3.client('rekognition', region_name=REGION)
s3          = boto3.client('s3', region_name=REGION)
dynamodb    = boto3.resource('dynamodb', region_name=REGION)


def get_images_from_s3(bucket_name):
    """Return a list of image keys from the S3 bucket"""
    images   = []
    response = s3.list_objects_v2(Bucket=bucket_name)

    if 'Contents' not in response:
        print("[WARN] No files found in bucket")
        return images

    for obj in response['Contents']:
        key = obj['Key']
        if key.lower().endswith(('.jpg', '.jpeg', '.png')):
            images.append(key)

    return images


def display_results(image_name, labels):
    """Print label results in a formatted table"""
    table = PrettyTable()
    table.field_names = ["Image", "Label", "Confidence"]

    for label in labels:
        table.add_row([
            image_name,
            label['Name'],
            f"{label['Confidence']:.2f}%"
        ])

    print(f"\nResults for: {image_name}")
    print(table)


def create_table_if_not_exists():
    """Create the DynamoDB table if it does not already exist"""
    try:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'image_name', 'KeyType': 'HASH'},
                {'AttributeName': 'label',       'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'image_name', 'AttributeType': 'S'},
                {'AttributeName': 'label',       'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits':  5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print(f"[OK] Table ready: {TABLE_NAME}")

    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'ResourceInUseException':
            print(f"[INFO] Table already exists: {TABLE_NAME}")
        else:
            print(f"[FAIL] Table error: {e}")


def store_in_dynamodb(image_name, labels):
    """Store each label and confidence score in DynamoDB"""
    table = dynamodb.Table(TABLE_NAME)

    for label in labels:
        table.put_item(Item={
            'image_name': image_name,
            'label':      label['Name'],
            'confidence': str(round(label['Confidence'], 2))
        })


def analyze_images(bucket_name):
    """Main pipeline: fetch images from S3, analyze with Rekognition, store results"""
    create_table_if_not_exists()

    images = get_images_from_s3(bucket_name)

    if not images:
        print("[FAIL] No valid images found in bucket")
        return

    for image in images:
        try:
            response = rekognition.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name':   image
                    }
                },
                MaxLabels=10,
                MinConfidence=70
            )

            labels = response['Labels']
            display_results(image, labels)
            store_in_dynamodb(image, labels)

        except Exception as e:
            print(f"[FAIL] Error processing {image}: {str(e)}")

    print("\n[OK] Analysis complete. Results stored in DynamoDB.")


if __name__ == "__main__":
    analyze_images(BUCKET_NAME)