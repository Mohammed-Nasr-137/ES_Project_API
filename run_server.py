import uvicorn
import database
from main import app
from fastapi import FastAPI

# ✅ Initialize database before running the server
database.init_db()

if __name__ == "__main__":
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
