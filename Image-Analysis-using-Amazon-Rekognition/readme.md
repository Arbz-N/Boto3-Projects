 Image Analysis with Amazon Rekognition
 
    Overview
    This project demonstrates an end-to-end image analysis pipeline using Amazon Rekognition. 
    Images stored in an S3 bucket are analyzed by Rekognition to detect labels and confidence scores. 
    Results are displayed in a formatted table and stored in DynamoDB for later querying.
    
    Local images folder
            |
            | upload_images.py
            v
    S3 Bucket
            |
            | analyze_images.py
            v
    Amazon Rekognition → Labels + Confidence Scores
            |
            v
    DynamoDB (Rekognition-Labels-Table)

Project Structure

    RekognitionLab/
    |
    |-- bucket-operation.py    # Create S3 and Upload images from local folder to S3
    |-- analyze_images.py      # Rekognition analysis pipeline + DynamoDB storage
    |-- requirements.txt       # Python dependencies
    |-- images/                # Place your .jpg / .jpeg / .png files here
    |
    |-- README.md

Prerequisites

    python3 --version
    pip install -r requirements.txt
    
    aws configure
    aws sts get-caller-identity

Task 2 — IAM Permissions
    
    The IAM user or role running these scripts needs the following policies attached:
    AmazonS3FullAccess
    AmazonRekognitionFullAccess
    AmazonDynamoDBFullAccess
    For production environments, scope these down to the minimum required actions.

Task 3 — Upload Images to S3

    Place your images in the ./images folder, then update the CONFIG in upload_images.py:
 
    LOCAL_FOLDER_PATH = "./images"
    REGION            = "your-region"

    python3 bucket-operation.py
    Expected output:
    Uploaded: dog.jpg
    Uploaded: car.jpg
    Uploaded: landscape.png

Task 4 — Run Rekognition Analysis

    Update the CONFIG in analyze_images.py:
    
    REGION      = "your-region"
    BUCKET_NAME = "your-bucket-name"

    python3 analyze_images.py

Expected output:

    [OK] Table ready: Rekognition-Labels-Table
    
    Results for: dog.jpg
    +----------+--------+------------+
    |  Image   | Label  | Confidence |
    +----------+--------+------------+
    | dog.jpg  | Dog    |   98.23%   |
    | dog.jpg  | Animal |   99.10%   |
    | dog.jpg  | Pet    |   95.40%   |
    +----------+--------+------------+
    
    [OK] Analysis complete. Results stored in DynamoDB.

    How It Works
    
    detect_labels Parameters

    rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket_name, 'Name': image}},
        MaxLabels=10,       # return at most 10 labels per image
        MinConfidence=70    # only include labels with 70% or higher confidence
    )

Cleanup

    Remove all objects from the bucket then delete it
    aws s3 rm s3://your-bucket-name --recursive
    aws s3 rb s3://your-bucket-name

    # Delete the DynamoDB table
    aws dynamodb delete-table \
      --table-name Rekognition-Labels-Table \
      --region your-region

License

    This project is licensed under the MIT License.