import boto3
from prettytable import PrettyTable

# AWS clients (reuse best practice)
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')


def get_images_from_s3(bucket_name):
    images = []

    response = s3.list_objects_v2(Bucket=bucket_name)
    # ↑ v2 use kiya (better + pagination support)

    if 'Contents' not in response:
        print("No files found in bucket ❌")
        return images

    for obj in response['Contents']:
        key = obj['Key']

        # ✅ Sirf images allow karo
        if key.lower().endswith(('.jpg', '.jpeg', '.png')):
            images.append(key)

    return images


def display_results(image_name, labels):
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


def analyze_images(bucket_name):
    images = get_images_from_s3(bucket_name)

    if not images:
        print("No valid images to process ❌")
        return

    for image in images:
        try:
            response = rekognition.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': bucket_name,
                        'Name': image
                    }
                },
                MaxLabels=10,          # ↑ max labels limit
                MinConfidence=70      # ↑ low confidence filter
            )

            display_results(image, response['Labels'])

        except Exception as e:
            print(f"Error processing {image}: {str(e)} ❌")


if __name__ == "__main__":
    bucket_name = "testing-lab-07554578"
    analyze_images(bucket_name)
