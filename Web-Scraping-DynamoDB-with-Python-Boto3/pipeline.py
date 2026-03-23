import boto3
import re
import requests
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
REGION     = "us-east-1"
TABLE_NAME = "My-Table"
URL        = "https://www.whatmobile.com.pk/"


def scrape_mobiles(url):
    """Website se mobile listings scrape karo"""
    print(f"  Scraping: {url}")
    try:
        headers = {'User-Agent': 'Chrome/58.0.3029.110'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('li', class_='product')

        mobiles = []
        for item in listings:
            try:
                name  = item.find('h4', class_='p4 biggertext').text.strip()
                price = item.find('span', class_='PriceFont').text.strip()
                mobiles.append({'name': name, 'price': price})
            except AttributeError:
                continue

        print(f"  Scraped {len(mobiles)} mobile listings")
        return mobiles

    except requests.RequestException as e:
        print(f"  Scraping failed: {e}")
        return []


def process_data(raw_text):
    """Data clean karo — special chars remove, lowercase"""
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', raw_text)
    return cleaned.lower().strip()


def create_table(dynamodb, table_name):
    """DynamoDB table create karo — agar exist karta ho skip karo"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'ID', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'ID', 'AttributeType': 'N'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"  Table '{table_name}' created and ready")
        return table

    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'ResourceInUseException':
            print(f"  Table '{table_name}' already exists — using it")
            return dynamodb.Table(table_name)
        print(f"  Table error: {e.response['Error']['Message']}")
        return None


def store_in_dynamodb(mobiles):
    """Mobile listings DynamoDB mein store karo"""
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table    = create_table(dynamodb, TABLE_NAME)

    if not table:
        return False

    for i, mobile in enumerate(mobiles, start=1):
        processed_name  = process_data(mobile['name'])
        processed_price = process_data(mobile['price'])

        table.put_item(Item={
            'ID':    i,
            'Name':  processed_name,
            'Price': processed_price
        })

    print(f"  {len(mobiles)} items stored in DynamoDB")
    return True


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Web Scraping → DynamoDB Pipeline")
    print("=" * 50)

    # Step 1: Scrape
    print("\n[1] Scraping website...")
    mobiles = scrape_mobiles(URL)
    if not mobiles:
        print("  No data scraped. Exiting.")
        exit(1)

    # Step 2: Store
    print("\n[2] Storing in DynamoDB...")
    success = store_in_dynamodb(mobiles)

    print("\n" + "=" * 50)
    if success:
        print(f"  Pipeline complete! {len(mobiles)} items in DynamoDB")
    else:
        print("  Pipeline failed")
    print("=" * 50)