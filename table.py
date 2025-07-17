import boto3

dynamodb = boto3.client("dynamodb", region_name="ap-south-1")

response = dynamodb.create_table(
    TableName="AttendanceRecords",
    KeySchema=[
        {"AttributeName": "Name", "KeyType": "HASH"},       # Partition key
        {"AttributeName": "Timestamp", "KeyType": "RANGE"}  # Sort key
    ],
    AttributeDefinitions=[
        {"AttributeName": "Name", "AttributeType": "S"},
        {"AttributeName": "Timestamp", "AttributeType": "S"}
    ],
    ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
)

print("✅ Table recreated successfully.")
