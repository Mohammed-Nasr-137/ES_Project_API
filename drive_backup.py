import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = "service-account.json"

# Define Google Drive folder ID where backups will be stored (Optional: Use root if not needed)
DRIVE_FOLDER_ID = "your_google_drive_folder_id_here"  # Replace with your folder ID (or leave None for root)

# Authenticate Google Drive API
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive.file"]
)

service = build("drive", "v3", credentials=creds)

# Backup file path
backup_file = "backup/database_backup.sqlite"

# Upload file to Google Drive
file_metadata = {
    "name": os.path.basename(backup_file),
    "mimeType": "application/x-sqlite3",
}
if DRIVE_FOLDER_ID:
    file_metadata["parents"] = [DRIVE_FOLDER_ID]

media = MediaFileUpload(backup_file, mimetype="application/x-sqlite3")
file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

print(f"Backup uploaded successfully! File ID: {file.get('id')}")
