import boto3
import os
from dotenv import load_dotenv

# Load AWS credentials
load_dotenv()
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def create_table():
    table_name = os.getenv("DYNAMO_TABLE_NAME", "AttendanceTable")
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]

    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists.")
        return

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'RecordID', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'RecordID', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    table.wait_until_exists()
    print(f"✅ Table '{table_name}' created successfully.")

create_table()
