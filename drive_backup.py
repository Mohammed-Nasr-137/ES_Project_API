import os
from fastapi import FastAPI, UploadFile, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load Service Account JSON Key
SERVICE_ACCOUNT_FILE = "sonorous-saga-428116-n4-5057c666a671.json"  # Replace with your actual JSON file
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Initialize Google Drive API
drive_service = build("drive", "v3", credentials=creds)

# Define Google Drive Folder ID where backups will be stored
FOLDER_ID = "1uKkh8Ggfi4L8MNNS7sXPiTT5RrgQcUKD"  # Replace with your Google Drive folder ID

# Initialize FastAPI
app = FastAPI()

def upload_to_drive(file_path: str, file_name: str):
    """Uploads a file to Google Drive in the specified folder."""
    try:
        file_metadata = {
            "name": file_name,
            "parents": [FOLDER_ID]  # Store inside the designated folder
        }
        media = MediaFileUpload(file_path, mimetype="application/octet-stream")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Drive upload failed: {e}")

@app.post("/backup")
async def backup_db(file: UploadFile):
    """Endpoint to upload database backup to Google Drive."""
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Upload to Google Drive
        file_id = upload_to_drive(file_path, file.filename)

        # Remove temporary file
        os.remove(file_path)

        return {"message": "Backup uploaded successfully", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
