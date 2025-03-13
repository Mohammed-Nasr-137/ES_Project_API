import signal
import subprocess
import sys
import uvicorn
import database
import uvicorn
from main import app

def backup_and_exit():
    print("Server is shutting down. Running database backup...")
    subprocess.run(["python", "drive_backup.py"])  # Runs your backup script
    print("Backup completed. Exiting now.")
    sys.exit(0)

# ✅ Initialize database before running the server
database.init_db()

# Catch termination signals (SIGTERM from Koyeb)
signal.signal(signal.SIGTERM, lambda signum, frame: backup_and_exit())
signal.signal(signal.SIGINT, lambda signum, frame: backup_and_exit())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Corrected

    # uvicorn.run("main:app", host="192.168.120.88", port=8000, reload=True)
