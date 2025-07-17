# 🧾 Project Setup & Reference Documentation

**Project Title:** Face Recognition Attendance System using Streamlit and AWS
**Developer:** Indana Aditya
**Tools:** Python, Streamlit, AWS (S3, Rekognition, DynamoDB), Boto3, OpenCV

---

## 📁 1. Project Structure (Repository Layout)

```
face-recognition-attendance/
├── app.py                      # Main Streamlit web app
├── utils/
│   └── aws_helper.py           # Contains AWS S3, Rekognition, DynamoDB logic
├── .env                        # AWS credentials and admin password
├── requirements.txt            # Python dependencies
├── known_faces/                # (Optional for local test) known images
├── output/
│   ├── screenshots/            # Screenshots of UI
│   └── demo.mp4                # Demo video of working app
└── README.md                   # Project documentation
```

---

## ⚙️ 2. Prerequisites

* ✅ Python ≥ 3.8
* ✅ pip installed
* ✅ AWS account with:

  * IAM user or role with permissions for **S3**, **Rekognition**, and **DynamoDB**
* ✅ Webcam-enabled system

---

## 🔐 3. AWS Configuration

### Step 1: Create S3 Bucket

* Name: `known-faces-of-students-2025`
* Folders:

  * `known_faces/` → upload known faces (e.g., `aditya.jpg`)
  * `unknown/` → temporary folder for runtime uploads

### Step 2: Create Rekognition Permissions

* Rekognition must access the S3 bucket

### Step 3: Create DynamoDB Table

* Name: `AttendanceRecords`
* Partition key: `Name` (String)
* Sort key: `Timestamp` (String)

### Step 4: IAM User / Role

* Create an IAM user or role with the following managed policies:

  * `AmazonS3FullAccess`
  * `AmazonRekognitionFullAccess`
  * `AmazonDynamoDBFullAccess`

---

## 🔑 4. Setup `.env` File

Create a `.env` file in the root directory with:

```env
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
BUCKET_NAME=known-faces-of-students-2025
ADMIN_PASSWORD=your-secure-password
```

---

## 📦 5. Install Dependencies

Run this in your terminal:

```bash
pip install -r requirements.txt
```

---

## ▶️ 6. Run the App

```bash
python -m streamlit run app.py
```

* Click **Start Camera** to activate webcam.
* Click **Capture Image** to take a snapshot.
* System uploads the image to S3 and compares it with known faces.
* If matched, attendance is marked in DynamoDB with image URL and timestamp.

---

## 🔐 7. Admin Panel Features

Accessible from the same interface using the admin password.

### Admin Can:

* View all students who marked attendance today
* ✅ Download CSV of attendance
* ❌ Delete all records from DynamoDB

---

## 📽️ 8. Output & Evidence

### Screenshots:

Save in `output/screenshots/`:

* Live camera interface
* Successful match message
* Admin panel dashboard

### Video Demo:

Save in **output/** [![Art.png](https://github.com/22MH1A42G1/Face-Recognition-Attendance-System-repository-iship/blob/main/output/Art.png)](https://youtu.be/NtWbiVcd0cc)

---

## 🧠 Optional Enhancements

* Face registration module to auto-upload known images
* Attendance graph visualization (using Streamlit + matplotlib)
* Email notifications via SES or SMTP
* Deployment on EC2 or S3 with CloudFront

---

## 🧠 Credits

* **Developer:** Indana Aditya
* **Mentors:** Mohammad Shaifu Zama, Durga Prasad Setti
* **Institution:** Technical Hub, Aditya Engineering College


