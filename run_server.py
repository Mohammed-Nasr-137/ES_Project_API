import os
import subprocess
import uvicorn
import database
from main import app
from fastapi import FastAPI

def backup_db():
    """ Commit and push the database to GitHub before shutdown """
    print("🔄 Backing up database to GitHub...")

    # Configure Git (only needed once)
    os.system("git config --global user.email 'nmohmmed285@gmail.com'")
    os.system("git config --global user.name 'Mohammed-Nasr-137'")

    # Set GitHub authentication
    github_token = os.getenv("GITHUB_PAT")  # Get GitHub token from environment
    if not github_token:
        print("❌ GITHUB_PAT is not set! Skipping backup.")
        return

    repo_url = f"https://Mohammed-Nasr-137:{github_token}@github.com/Mohammed-Nasr-137/ES_Project_API.git"
    os.system(f"git remote set-url origin {repo_url}")

    # Check if there are changes
    status = subprocess.getoutput("git status --porcelain")
    if not status:
        print("✅ No changes in database, skipping commit.")
        return

    # Add, commit, and push the database file
    os.system("git add sensor_data.db")
    os.system('git commit -m "🔄 Auto-backup database before shutdown"')
    os.system("git push origin main")  # Change 'main' if using another branch

    print("✅ Database successfully backed up!")

# ✅ Initialize database before running the server
database.init_db()

# ✅ Hook into FastAPI shutdown event
@app.on_event("shutdown")
def shutdown_event():
    backup_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
