# Web Scraping → DynamoDB with Python Boto3:

Overview

    This is a hands-on project that builds a complete data pipeline in a single Python script: 
    scrape mobile phone listings from whatmobile.com.pk, clean the data, and store it in AWS DynamoDB.
    It combines requests + BeautifulSoup for scraping with boto3 for cloud storage.
    Key highlights:
    
    requests fetches the page with a browser User-Agent header to avoid 403 blocks
    BeautifulSoup parses <li class="product"> listings for name and price
    re.sub() cleans all special characters — stores lowercase alphanumeric only
    DynamoDB table auto-created with table_exists waiter before inserting
    ResourceInUseException handled gracefully — reuses existing table
    Full scrape → process → store pipeline in one python3 pipeline.py run

Project Structure

    Web-Scraping-DynamoDB-with-Python-Boto3/
    │
    ├── pipeline.py         # Main script — scrape → clean → store
    ├── requirements.txt    # Dependencies
    │
    └── README.md

Prerequisites

    Requirement               Check
    
    Python 3.8+               python3 --version
    AWS CLI                   aws sts get-caller-identity
    AWS credentials           IAM user with DynamoDB permissions

Architecture
 
        whatmobile.com.pk
               │
               │  requests.get() + BeautifulSoup
               ▼
          scrape_mobiles()
          ├── <li class="product">
          │   ├── <h4 class="p4 biggertext"> → name
          │   └── <span class="PriceFont">   → price
          └── returns: [{'name': '...', 'price': '...'}, ...]
               │
               │  process_data() — re.sub clean + lowercase
               ▼
          store_in_dynamodb()
          ├── create_table()  → My-Table (ID: Number PK)
          │   └── waiter: table_exists
          └── table.put_item() × N
               │
               ▼
          DynamoDB Table: My-Table
          ┌────┬────────────────────┬──────────────┐
          │ ID │ Name               │ Price        │
          ├────┼────────────────────┼──────────────┤
          │  1 │ samsung galaxy s24 │ rs 289999    │
          │  2 │ iphone 15 pro      │ rs 459999    │
          │ .. │ ...                │ ...          │
          └────┴────────────────────┴──────────────┘

 Setup
bash# Create and activate virtual environment
python3 -m venv scrape-env
source scrape-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
pip show boto3 requests beautifulsoup4

# AWS credentials check
aws sts get-caller-identity  # 

 Run
python3 pipeline.py

Expected Output

==================================================
  Web Scraping → DynamoDB Pipeline
==================================================

[1] Scraping website...
  Scraping: https://www.whatmobile.com.pk/
  Scraped 20 mobile listings ✅

[2] Storing in DynamoDB...
  Table 'My-Table' created and ready ✅
  20 items stored in DynamoDB ✅

==================================================
  Pipeline complete! 20 items in DynamoDB ✅
==================================================


Code Concepts

    Scraping with User-Agent Header
    headers = {'User-Agent': 'Chrome/58.0.3029.110'}
    response = requests.get(url, headers=headers, timeout=10)
    # Without User-Agent → 403 Forbidden (site blocks bots)
    # With User-Agent    → site thinks it's a browser 

    Data Cleaning with Regex
    def process_data(raw_text):
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', raw_text)
        return cleaned.lower().strip()
    
    # Input:  "Samsung Galaxy S24 Ultra – Rs. 289,999/-"
    # Output: "samsung galaxy s24 ultra  rs 289999"

    DynamoDB Table — Handle Already Exists
    except ClientError as e:
        code = e.response['Error']['Code']
        if code == 'ResourceInUseException':
            # Table already exists — reuse it
            return dynamodb.Table(table_name)

    Verify Data in DynamoDB
    bash# Console se verify karo
    aws dynamodb scan \
      --table-name My-Table \
      --region us-east-1 \
      --query 'Items[*].{ID:ID.N,Name:Name.S,Price:Price.S}' \
      --output table

Cleanup
bash# Delete DynamoDB table
aws dynamodb delete-table \
  --table-name My-Table \
  --region us-east-1

echo "DynamoDB table deleted "

# Deactivate venv
deactivate
rm -rf scrape-env/

📄 License
This project is licensed under the MIT License.