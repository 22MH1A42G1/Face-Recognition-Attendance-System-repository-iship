# app.py

import streamlit as st # ✅ For Streamlit UI

import cv2 # ✅ For video capture

import numpy as np # ✅ For image processing
from PIL import Image # ✅ For image processing

import tempfile # ✅ For temporary file handling
import os # ✅ For file handling

from dotenv import load_dotenv # ✅ For loading environment variables

from datetime import datetime  # ✅ For today's date filtering

import pandas as pd            # ✅ If you're using dataframe to display

import boto3                   # ✅ For DynamoDB admin access

import io # ✅ For in-memory file handling

import os # ✅ To handle file paths


# ---------------- Import Required Libraries ---------------- #
# Import custom AWS helper functions
from utils.aws_helper import upload_to_s3, compare_faces, mark_attendance


# ---------------- Load Environment ---------------- #
load_dotenv()
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID") 
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET = os.getenv("S3_BUCKET")
UNKNOWN_FOLDER = "unknown"
KNOWN_FOLDER = "known_faces"


# ---------------- Page Configuration ---------------- #
st.set_page_config(page_title="🎯 Face Recognition Attendance", layout="wide")
st.title("🎯 Face Recognition Attendance System")
st.markdown("---")

# ---------------- Session State Initialization ---------------- #
for key in ["camera_active", "image_captured", "captured_image", "recognized_name"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "captured_image" else None

# ---------------- Layout ---------------- #
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎛 Controls")
    start_btn = st.button("📷 Start Camera")
    capture_btn = st.button("🖼️ Capture Image")
    clear_btn = st.button("🔁 Reset")

    st.markdown("---")
    st.info(
        "### ℹ️ Instructions:\n"
        "- Click **Start Camera** to activate webcam.\n"
        "- Click **Capture Image** to save a snapshot.\n"
        "- Face will be auto-recognized and marked present."
    )

    if st.session_state.recognized_name:
        st.success(f"✅ Attendance marked for **{st.session_state.recognized_name}**")
    elif st.session_state.image_captured and not st.session_state.recognized_name:
        st.error("❌ Face not recognized.")

with col2:
    st.subheader("📸 Live Camera / Captured Image")
    camera_placeholder = st.empty()

# ---------------- Button Logic ---------------- #
if start_btn:
    st.session_state.camera_active = True
    st.session_state.image_captured = False
    st.session_state.recognized_name = None

if clear_btn:
    for key in ["camera_active", "image_captured", "captured_image", "recognized_name"]:
        st.session_state[key] = False if key != "captured_image" else None
    st.rerun()


# ---------------- Camera Stream & Capture ---------------- #
if st.session_state.camera_active and not st.session_state.image_captured:
    cap = cv2.VideoCapture(0)
    frame_window = camera_placeholder.image([])

    while True:
        ret, frame = cap.read()
        if not ret:
            st.warning("⚠️ Unable to access webcam.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_window.image(frame_rgb, channels="RGB", use_container_width=True)

        if capture_btn:
            cap.release()
            st.session_state.camera_active = False
            st.session_state.image_captured = True

            temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            Image.fromarray(frame_rgb).save(temp_file.name)
            st.session_state.captured_image = temp_file.name

            camera_placeholder.image(
                frame_rgb, caption="📸 Captured Image", use_container_width=True
            )

            # Upload to S3 and recognize
            uploaded_filename = os.path.basename(temp_file.name)
            with open(temp_file.name, "rb") as img_file:
                s3_key = upload_to_s3(img_file, uploaded_filename, BUCKET, UNKNOWN_FOLDER)

            recognized_name = compare_faces(BUCKET, f"{UNKNOWN_FOLDER}/{uploaded_filename}")
            if recognized_name:
                mark_attendance(recognized_name, BUCKET, f"{UNKNOWN_FOLDER}/{uploaded_filename}")
                st.session_state.recognized_name = recognized_name
            else:
                st.session_state.recognized_name = None

            st.rerun()
            break

else:
    if not st.session_state.captured_image:
        camera_placeholder.info("📡 Camera not started.")
    elif st.session_state.image_captured:
        img = Image.open(st.session_state.captured_image)
        camera_placeholder.image(img, caption="📸 Captured Image", use_container_width=True)

# ---------------- Admin Section ---------------- #

with st.sidebar.expander("🔐 Admin Login", expanded=False):
    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password == "admin@2025":  # Change as needed or move to .env
            dynamodb = boto3.resource('dynamodb', region_name=os.getenv("AWS_REGION"))
            table = dynamodb.Table("AttendanceTable")

            # Filter only today's attendance
            today = datetime.now().date().isoformat()
            response = table.scan()
            items = response.get("Items", [])
            todays_records = [i for i in items if i["TimeStamp"].startswith(today)]

            if todays_records:
                df = pd.DataFrame(todays_records)
                df = df[["StudentName", "TimeStamp", "Status", "ImageURL", "RecordID", "Department", "Year-PassOut"]]  # You can include "ImageURL" too if needed
                st.dataframe(df, use_container_width=True)

                # Convert DataFrame to CSV
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()

                # Download button
                st.download_button(
                    label="⬇️ Download Today's Attendance as CSV",
                    data=csv_data,
                    file_name=f"attendance_{today}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ℹ️ No attendance records found for today.")
        else:
            st.error("❌ Invalid password")

# -------------------- End of Streamlit App -------------------- #
