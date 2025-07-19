import boto3
import os
import logging
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime

# -------------------- Setup Logging -------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------- Load Environment Variables -------------------- #
load_dotenv()

AWS_REGION         = os.getenv("AWS_REGION")
ACCESS_KEY         = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY         = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET          = os.getenv("S3_BUCKET", "known-faces-of-students-2025")
UNKNOWN_FOLDER     = os.getenv("UNKNOWN_FOLDER", "unknown")
KNOWN_FOLDER       = os.getenv("KNOWN_FOLDER", "known_faces")
DYNAMO_TABLE_NAME  = os.getenv("DYNAMO_TABLE_NAME", "AttendanceRecords")  # ✅ FIXED: Replaced hardcoded value

# -------------------- AWS Clients -------------------- #
try:
    s3 = boto3.client(
        's3',
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    rekognition = boto3.client(
        'rekognition',
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
except Exception as e:
    logging.error("❌ Failed to initialize AWS clients: %s", e)
    raise

# -------------------- Upload File to S3 -------------------- #
def upload_to_s3(file, filename, bucket, folder):
    try:
        key = f"{folder}/{filename}"
        s3.upload_fileobj(file, bucket, key)
        logging.info(f"✅ Uploaded file to s3://{bucket}/{key}")
        return key
    except Exception as e:
        logging.error("❌ Error uploading file to S3: %s", e)
        return None

# -------------------- Compare Face with Rekognition -------------------- #
def compare_faces(bucket, uploaded_key):
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=f"{KNOWN_FOLDER}/")
        known_files = response.get('Contents', [])

        for obj in known_files:
            source_key = obj['Key']
            if source_key.endswith('/') or source_key == f"{KNOWN_FOLDER}/":
                continue  # Skip folders

            result = rekognition.compare_faces(
                SourceImage={'S3Object': {'Bucket': bucket, 'Name': source_key}},
                TargetImage={'S3Object': {'Bucket': bucket, 'Name': uploaded_key}},
                SimilarityThreshold=85
            )

            matches = result.get("FaceMatches", [])
            if matches:
                matched_name = os.path.basename(source_key).split('.')[0]
                logging.info(f"🎯 Face matched with: {matched_name}")
                return matched_name

        logging.warning("⚠️ No matching faces found.")
        return None

    except Exception as e:
        logging.error("❌ Error comparing faces: %s", e)
        return None

# -------------------- Mark Attendance in DynamoDB -------------------- #
def mark_attendance(name, bucket, uploaded_key):
    try:
        table = dynamodb.Table(DYNAMO_TABLE_NAME)  # ✅ FIXED: used env variable instead of hardcoded value

        item = {
            "RecordID": str(uuid4()),  # ✅ Primary Key (recommended to make this HASH key)
            "StudentName": name,
            "TimeStamp": datetime.now().isoformat(),  # ✅ Consistent key naming
            "Status": "Present",
            "ImageURL": f"https://{bucket}.s3.amazonaws.com/{uploaded_key}",  # ✅ FIXED: changed s3:// to https:// for UI display
            "Department": "CSE - AIML",  # Optional
            "Year-PassOut": "2022-2026"  # Optional
        }

        table.put_item(Item=item)
        logging.info(f"✅ Attendance marked for: {name}")
        return True

    except Exception as e:
        logging.error("❌ Error marking attendance: %s", e)
        return False
