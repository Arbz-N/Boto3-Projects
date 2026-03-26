# Lab 1: Image Analysis using Amazon Rekognition
## S3 + Boto3 + Rekognition Complete Pipeline
> **Objective:** Is lab ka goal hai images ko S3 par upload karna aur Amazon Rekognition se unka AI-based analysis karna.
> **Independent Lab:** Har lab standalone hai — koi dependency nahi. ✅
---

# CONCEPTS

## Concept 1: Amazon S3 (Simple Storage Service)
```
→ Object storage service hai
→ Files ko "bucket" mein store karta hai
→ Highly scalable & durable

Structure:

Bucket
  ├── image1.jpg
  ├── image2.png

Analogy:
→ Bucket = Folder
→ Object = File

✅ Easy storage
❌ Public access galat configure ho sakta hai ⚠️
```

## Concept 2: Amazon Rekognition
```
→ AI service jo images analyze karta hai
→ Labels detect karta hai (car, person, dog, etc.)
→ Confidence score deta hai

Flow:

S3 Image → Rekognition → Labels + Confidence

Example:
Dog.jpg → Dog (98%)

✅ No ML training needed
❌ Paid service (usage based)
```

## Concept 3: Boto3 (AWS SDK for Python)
```
→ Python library AWS services use karne ke liye
→ CLI ka programmatic version

Example:
→ S3 upload
→ Rekognition call

Analogy:
→ AWS CLI = Manual commands
→ Boto3 = Automation script

✅ Automation friendly
❌ Credentials misconfigure ho sakte hain
```

## Concept 4: IAM Permissions
```
→ AWS access control system
→ Define karta hai kon kya kar sakta hai

Example:
→ S3 access
→ Rekognition access

⚠️ Least privilege use karo

❌ FullAccess production mein risky hai
```

---

# LAB — Step by Step

## Prerequisites
- AWS Account
- AWS CLI installed
- Python installed
- Boto3 installed
- Images folder ready

---

## Task 1: AWS Setup

### Step 1.1 — S3 Bucket Create karo
```
→ AWS Console → S3 → Create Bucket
→ Unique naam do
→ Region select karo
→ Default settings use karo
```

### Step 1.2 — AWS CLI configure karo
```bash
aws configure
# ↑ AWS CLI setup command

# Enter credentials:
# Access Key = AWS se milti hai
# Secret Key = secure key
# Region = apka region (e.g. us-east-1)
# Output = json (default)
```

---

## Task 2: Upload Images to S3

### Step 2.1 — Python Script

```python
import boto3
import os

# S3 client create kar rahe hain
s3 = boto3.client('s3')

def upload_images_to_s3(bucket_name, local_folder_path):
    for root, dirs, files in os.walk(local_folder_path):
        # ↑ recursively folder traverse karta hai
        
        for file in files:
            local_file_path = os.path.join(root, file)
            # ↑ full path create

            s3_file_key = os.path.relpath(local_file_path, local_folder_path)
            # ↑ S3 mein relative path maintain karega

            s3.upload_file(local_file_path, bucket_name, s3_file_key)
            # ↑ file upload ho rahi hai

if __name__ == "__main__":
    bucket_name = "your-bucket-name"
    local_folder_path = "./images"
    upload_images_to_s3(bucket_name, local_folder_path)
```

### Step 2.2 — Run Script
```bash
python upload_images_to_s3.py
# ↑ script run karega aur images S3 pe upload hongi
```

---

## Task 3: Rekognition Analysis

### Step 3.1 — IAM Role / Permissions
```
→ IAM → Roles → Create Role
→ Service: Rekognition
→ Attach Policy: AmazonRekognitionFullAccess

⚠️ Production mein limited policy use karo
```

### Step 3.2 — Install dependency
```bash
pip install boto3 prettytable
# ↑ boto3 AWS ke liye
# ↑ prettytable output formatting ke liye
```

### Step 3.3 — Analysis Script

```python
import boto3
from prettytable import PrettyTable

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

def get_images_from_s3(bucket_name):
    response = s3.list_objects(Bucket=bucket_name)
    # ↑ bucket ke andar objects list karega
    
    return [obj['Key'] for obj in response.get('Contents', [])]


def display_results(image_name, labels):
    table = PrettyTable()
    table.field_names = ["Image", "Label", "Confidence"]

    for label in labels:
        table.add_row([
            image_name,
            label['Name'],
            f"{label['Confidence']:.2f}%"
        ])

    print(table)


def analyze_images(bucket_name):
    images = get_images_from_s3(bucket_name)

    for image in images:
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket_name,
                    'Name': image
                }
            }
        )
        # ↑ Rekognition ko S3 image diya

        display_results(image, response['Labels'])


if __name__ == "__main__":
    bucket_name = "your-bucket-name"
    analyze_images(bucket_name)
```

### Step 3.4 — Run Script
```bash
python analyze_images.py
# ↑ AI analysis start ho jayega
```

---

## Task 4: Output Samajhna
```
Output Table:

Image       Label      Confidence
---------------------------------
dog.jpg     Dog        98.23%
dog.jpg     Animal     99.10%

→ Multiple labels possible hain
→ Confidence jitni high utna accurate
```

---

# REAL ERRORS SECTION

```
Error 1: NoCredentialsError
────────────────────────────────────────
Cause: AWS CLI configure nahi hai
Fix:
aws configure ✅
```

```
Error 2: AccessDeniedException
────────────────────────────────────────
Cause: IAM permissions missing
Fix:
AmazonRekognitionFullAccess attach karo ✅
```

```
Error 3: NoSuchBucket
────────────────────────────────────────
Cause: Bucket naam galat
Fix:
Correct bucket name use karo ✅
```

```
Error 4: list_objects empty
────────────────────────────────────────
Cause: Bucket mein images nahi hain
Fix:
Upload script dobara run karo ✅
```

---

# CLEANUP

```bash
# Bucket delete karne ke liye
aws s3 rm s3://your-bucket-name --recursive
# ↑ pehle saari files delete

aws s3 rb s3://your-bucket-name
# ↑ bucket delete
```

---

# Conclusion

```
→ Images S3 mein upload ki
→ Rekognition se analyze ki
→ Labels + confidence nikala

```

