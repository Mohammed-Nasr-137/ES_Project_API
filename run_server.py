import uvicorn
import database
import uvicorn
import database  # Ensure database is initialized before starting the server

# ✅ Initialize database before running the server
database.init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # Corrected

    # uvicorn.run("main:app", host="192.168.120.88", port=8000, reload=True)
