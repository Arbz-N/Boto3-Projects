import boto3
import uuid
from botocore.exceptions import ClientError
import os

s3 = boto3.client('s3')

def create_bucket(bucket_name, region="us-east-1"):
    try:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                }
            )
        print(f" Bucket created: {bucket_name}")
        return True

    except ClientError as e:
        print(f" Error creating bucket: {e.response['Error']['Message']}")
        return False


def upload_images_to_s3(bucket_name, local_folder_path):

    if not os.path.exists(local_folder_path):
        print(" Folder exist nahi karta")
        return

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            if not file.endswith((".jpg", ".jpeg", ".png")):
                continue
            local_file_path = os.path.join(root, file)
            s3_file_key = os.path.relpath(local_file_path, local_folder_path)

            try:
                s3.upload_file(local_file_path, bucket_name, s3_file_key)
                print(f"⬆ Uploaded: {s3_file_key}")

            except ClientError as e:
                print(f" Upload failed: {file} → {e}")


if __name__ == "__main__":

    bucket_name = f"boto3-lab-{uuid.uuid4().hex[:8]}"
    local_folder_path = "./images"

    print("=" * 50)
    print("S3 Manager — Boto3 Lab")
    print("=" * 50)

    print("1. Creating bucket...")
    if create_bucket(bucket_name):

        print("2. Uploading images...")
        upload_images_to_s3(bucket_name, local_folder_path)

    else:
        print(" Bucket creation failed — upload skip ho gaya")
