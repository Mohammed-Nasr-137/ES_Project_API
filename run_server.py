import uvicorn
import database
from main import app
from fastapi import FastAPI

# ✅ Initialize database before running the server


if __name__ == "__main__":
    database.init_db()
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
