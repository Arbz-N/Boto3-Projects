# AWS S3 Management with Python Boto3

    Overview
    This is a hands-on project that demonstrates AWS S3 management using Boto3 — the official AWS SDK for Python. 
    It covers creating a virtual environment, configuring AWS credentials, and performing full S3 CRUD operations: list buckets, create bucket, upload file, list objects, and delete bucket with cleanup.
    Key highlights:
    
    Python virtual environment for clean dependency isolation
    Boto3 s3.client used for all S3 operations
    Unique bucket name generated with uuid4 to avoid conflicts
    ClientError exception handling on every operation
    Full create → upload → list → delete lifecycle in one script run
    Cleanup covered both locally (venv, files) and on AWS (leftover buckets)


Project Structure:

    AWS-S3-Management-with-Python-Boto3/
    │
    ├── s3_manager.py       # Main script — full S3 CRUD operations
    ├── requirements.txt    # boto3 dependency
    │
    └── README.md

 Prerequisites

    Requirement            Check 

    Python3.8+             python3 --version 
    pip                    pip3 --version
    AWS CLI                aws --version
    AWS credentials        aws sts get-caller-identity

Architecture:
    
    Python Script (s3_manager.py)
           │
           │  boto3.client('s3')
           ▼
      AWS S3 API
      │
      ├── list_buckets()      → ListBuckets
      ├── create_bucket()     → CreateBucket
      ├── upload_file()       → PutObject
      ├── list_objects_v2()   → ListObjectsV2
      └── delete_bucket()     → DeleteObjects + DeleteBucket
    
      Bucket name: boto3-lab-{uuid4[:8]}  ← unique every run

Setup
Step 1 — Virtual Environment:

    Create and activate venv
    python3 -m venv boto3-lab
    source boto3-lab/bin/activate      # Linux/Mac
    # boto3-lab\Scripts\activate       # Windows
    
    # Prompt changes to:
    # (boto3-lab) user@machine:~$
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Verify
    pip list | grep boto3
    # boto3  1.xx.x 


Step 2 — AWS Configure:

    aws configure
    # AWS Access Key ID     : AKIA...
    # AWS Secret Access Key : ****
    # Default region name   : us-east-1
    # Default output format : json
    
    # Verify
    aws sts get-caller-identity
    # Account ID + ARN 

Run the Script:

    python3 s3_manager.py

Expected Output
==================================================
  S3 Manager — Boto3 Lab
==================================================

1. Existing Buckets:
  Total buckets: 3
  → my-existing-bucket-1
  → my-existing-bucket-2

2. Creating new bucket...
  Bucket created: boto3-lab-a1b2c3d4

3. Uploading file...
  Uploaded: boto3-test.txt → s3://boto3-lab-a1b2c3d4/test/boto3-test.txt

4. Listing objects...
  Objects in boto3-lab-a1b2c3d4: 1
  → test/boto3-test.txt (31 bytes)

5. Cleanup...
  Deleted object: test/boto3-test.txt
  Bucket deleted: boto3-lab-a1b2c3d4

==================================================
  Lab complete! 
==================================================

Code Walkthrough

    S3 Client
    
    pythons3 = boto3.client('s3')
    # Uses credentials from ~/.aws/credentials or environment variables
    # Region from ~/.aws/config or AWS_DEFAULT_REGION env var

    Unique Bucket Name
    pythonbucket_name = f"boto3-lab-{uuid.uuid4().hex[:8]}"
    # Example: boto3-lab-a1b2c3d4
    # uuid4 = random UUID → no name conflicts between runs
    
    Error Handling
    from botocore.exceptions import ClientError

    try:
        s3.create_bucket(Bucket=bucket_name)
    except ClientError as e:
        print(e.response['Error']['Message'])
    # Every S3 operation wrapped in try/except 

    Delete Bucket (Objects First)
    python# S3 bucket delete karne se pehle sab objects delete karne padte hain
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response.get('Contents', []):
        s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    s3.delete_bucket(Bucket=bucket_name)

Cleanup:

    bash# Deactivate venv
    deactivate
    
    # Delete local files
    rm -f boto3-test.txt
    rm -rf boto3-lab/
    
    # Check for leftover AWS buckets
    aws s3 ls | grep boto3-lab
    
    # Force delete if any remain
    aws s3 rb s3://boto3-lab-XXXXXXXX --force

License:

    This project is licensed under the MIT License.