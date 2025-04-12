import uvicorn
import database
import uvicorn
from main import app

# ✅ Initialize database before running the server
database.init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Corrected
    uvicorn.run("/frontend/app:app", host="0.0.0.0", port=8000, reload=True)

    # uvicorn.run("main:app", host="192.168.120.88", port=8000, reload=True)
