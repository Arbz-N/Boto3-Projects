import boto3
import uuid
from botocore.exceptions import ClientError


def create_s3_client():
    return boto3.client('s3')


def list_buckets(s3):
    response = s3.list_buckets()
    buckets = response['Buckets']
    print(f"\n  Total buckets: {len(buckets)}")
    for bucket in buckets:
        print(f"  → {bucket['Name']}")
    return buckets


def create_bucket(s3, bucket_name):
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"  Bucket created: {bucket_name}")
        return True
    except ClientError as e:
        print(f"  Error: {e.response['Error']['Message']}")
        return False


def upload_file(s3, bucket_name, local_file, s3_key):
    try:
        s3.upload_file(local_file, bucket_name, s3_key)
        print(f"  Uploaded: {local_file} → s3://{bucket_name}/{s3_key}")
    except ClientError as e:
        print(f"  Upload failed: {e.response['Error']['Message']}")


def list_objects(s3, bucket_name):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        objects = response.get('Contents', [])
        print(f"\n  Objects in {bucket_name}: {len(objects)}")
        for obj in objects:
            print(f"  → {obj['Key']} ({obj['Size']} bytes)")
    except ClientError as e:
        print(f"  Error: {e.response['Error']['Message']}")


def delete_bucket(s3, bucket_name):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        for obj in response.get('Contents', []):
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            print(f"  Deleted object: {obj['Key']}")

        s3.delete_bucket(Bucket=bucket_name)
        print(f"  Bucket deleted: {bucket_name}")
    except ClientError as e:
        print(f"  Error: {e.response['Error']['Message']}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    s3 = create_s3_client()
    bucket_name = f"boto3-lab-{uuid.uuid4().hex[:8]}"

    print("=" * 50)
    print("  S3 Manager — Boto3 Lab")
    print("=" * 50)

    print("\n1. Existing Buckets:")
    list_buckets(s3)

    print("\n2. Creating new bucket...")
    create_bucket(s3, bucket_name)

    print("\n3. Uploading file...")
    with open("boto3-test.txt", "w") as f:
        f.write("Hello from Boto3 S3 Manager!\n")
    upload_file(s3, bucket_name, "boto3-test.txt", "test/boto3-test.txt")

    print("\n4. Listing objects...")
    list_objects(s3, bucket_name)

    print("\n5. Cleanup...")
    delete_bucket(s3, bucket_name)

    print("\n" + "=" * 50)
    print("  Lab complete!")
    print("=" * 50)