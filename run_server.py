import os
import subprocess
import uvicorn
import database
import uvicorn
from main import app

def backup_db():
    """ Commit and push the database to GitHub before shutdown """
   # Configure Git (only needed once)
    os.system("git config --global user.email 'nmohmmed285@gmail.com'")
    os.system("git config --global user.name 'Mohammed-Nasr-137'")

    # Add GitHub token for authentication
    repo_url = "https://Mohammed-Nasr-137:${GITHUB_PAT}@github.com/Mohammed-Nasr-137/ES_Project_API.git"
    os.system(f"git remote set-url origin {repo_url}")

    # Add, commit, and push the database file
    os.system("git add sensor_data.db")
    os.system('git commit -m "🔄 Auto-backup database before shutdown"')
    os.system("git push origin main")  # Change 'main' to your branch

# ✅ Initialize database before running the server
database.init_db()

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Corrected

        # uvicorn.run("main:app", host="192.168.120.88", port=8000, reload=True)
    except KeyboardInterrupt:
        print("🔄 Backing up database to GitHub...")
        backup_db()
        print("✅ Database backed up!")
