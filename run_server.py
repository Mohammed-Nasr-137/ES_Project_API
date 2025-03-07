import uvicorn
import database
from main import app


if __name__ == "__main__":
    database.init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run("main:app", host="192.168.120.88", port=8000, reload=True)
