import uvicorn
from main import app as fastapi_app
from app import app as dash_app
from fastapi.middleware.wsgi import WSGIMiddleware
import database

# Initialize the database
print("\U0001F504 Initializing database...")
database.init_db()
print("\u2705 Database initialized with tables!")

# Mount the Dash app on a subpath (e.g. /dashboard)
fastapi_app.mount("/dashboard", WSGIMiddleware(dash_app.server))
app = fastapi_app  # 👈 this is what Koyeb needs
if __name__ == "__main__":
    uvicorn.run("run_server:fastapi_app", host="0.0.0.0", port=8000, reload=True)
