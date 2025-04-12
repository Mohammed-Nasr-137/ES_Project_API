from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import database, models, schemas, crud
import json
import database
import os
import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import dash_bootstrap_components as dbc

app = FastAPI()

# Initialize the database
# print("🔄 Initializing database...")
# database.init_db()  # ✅ Ensure database is initialized
# print("✅ Database initialized with tables!")
# models.Base.metadata.create_all(bind=database.engine)


# WebSocket connections storage
active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(database.get_db)):
    """ WebSocket: Handles real-time communication """
    
    await websocket.accept()  # Accept the WebSocket connection
    active_connections.append(websocket)  # Store it
    
    try:
        while True:
            data = await websocket.receive_text()  # Receive data
            data_json = json.loads(data)
            # print(f"Received: {data}")

            if "command" in data_json:  
                # Future handling for commands (like start/stop sampling)
                continue

            if "command" in data_json:  
                # Future handling for commands (like start/stop sampling)
                continue  

            # Validate & store sensor data
            db = database.SessionLocal()
            sensor_data = schemas.SensorDataCreate(**data_json)
            crud.create_sensor_data(db, sensor_data)
            db.close()

            # # Validate data format
            # if "point_id" not in data_json or "depth" not in data_json:
            #     await websocket.send_text("Invalid data format!")
            #     continue

            # # Convert JSON to schema
            # data_obj = schemas.SensorDataCreate(
            #     point_id = data_json["point_id"],
            #     depth = data_json["depth"]
            # )

            # # Store data in the database
            # db_data = crud.create_sensor_data(db, data_obj)

            # Send back a response
            # await websocket.send_text(f"Server received: {data}")

    except WebSocketDisconnect:
        active_connections.remove(websocket)  # Remove disconnected clients
        print("Client disconnected")


@app.websocket("/ws/control")
async def websocket_control(websocket: WebSocket):
    """WebSocket for GUI to send commands to ESP32"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            command = await websocket.receive_text()
            
            # Forward command to ESP32 clients
            for conn in active_connections:
                try:
                    await conn.send_text(command)
                except:
                    active_connections.remove(conn)

    except WebSocketDisconnect:
        active_connections.remove(websocket)

    

@app.post("/sensor_data/", response_model=schemas.SensorDataResponse)
def create_sensor_data(data: schemas.SensorDataCreate, db: Session = Depends(database.get_db)):
    """Receives sensor data and stores it in the database"""
    db_data = crud.create_sensor_data(db, data)
    
    # Send real-time updates via WebSocket
    disconnected_clients = []
    for connection in active_connections:
        try:
            # Using await inside a normal function is invalid, so we use an async task
            import asyncio
            asyncio.create_task(connection.send_json({
                "sensor_id": db_data.sensor_id,
                "point_id": db_data.point_id,
                "depth": db_data.depth,
                "timestamp": db_data.timestamp.isoformat()
            }))
        except WebSocketDisconnect:
            disconnected_clients.append(connection)

    # Remove disconnected clients
    for connection in disconnected_clients:
        active_connections.remove(connection)

    return db_data


DB_PATH = "sensor_data.db"
@app.get("/download-db")
def download_db():
    if os.path.exists(DB_PATH):
        return FileResponse(DB_PATH, filename="sensor_data.db", media_type="application/octet-stream")
    return {"error": "Database file not found"}


@app.get("/sensor_data/{point_id}", response_model=list[schemas.SensorDataResponse])
def get_sensor_data(point_id: int, limit: int = 10, db: Session = Depends(database.get_db)):
    """Fetches the latest sensor data for a given point"""
    return crud.get_sensor_data(db, point_id, limit)


# ---------------------------
# Config
# ---------------------------
API_URL = "https://shiny-deana-mohammednasr-4c86290b.koyeb.app/sensor_data/1"

# ---------------------------
# App Initialization
# ---------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Lake Depth Dashboard"

# ---------------------------
# Helper Functions
# ---------------------------
def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return pd.DataFrame()

def filter_data(df, range_value):
    now = datetime.utcnow()
    if range_value == "day":
        since = now - timedelta(days=1)
    elif range_value == "week":
        since = now - timedelta(weeks=1)
    else:
        since = now - timedelta(days=30)
    return df[df["timestamp"] >= since]

# ---------------------------
# Layout
# ---------------------------
app.layout = dbc.Container([
    html.H1("Lake Water Depth Monitoring", className="my-3 text-center text-primary"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="time-range",
                options=[
                    {"label": "Last Day", "value": "day"},
                    {"label": "Last Week", "value": "week"},
                    {"label": "Last Month", "value": "month"},
                ],
                value="week",
                clearable=False,
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Button("Download Report", id="download-btn", className="btn btn-success mb-3"),
            dcc.Download(id="download")
        ], width=4),
    ], justify="center"),

    dcc.Graph(id="depth-graph"),

    dbc.Row([
        dbc.Col(html.Div(id="max-depth", className="alert alert-info")),
        dbc.Col(html.Div(id="min-depth", className="alert alert-warning"))
    ], className="my-3")

], fluid=True)

# ---------------------------
# Callbacks
# ---------------------------
@app.callback(
    [Output("depth-graph", "figure"),
     Output("max-depth", "children"),
     Output("min-depth", "children")],
    Input("time-range", "value")
)
def update_graph(range_value):
    df = fetch_data()
    if df.empty:
        return px.line(), "No data", "No data"

    df_filtered = filter_data(df, range_value)

    fig = px.line(df_filtered, x="timestamp", y="depth", title="Water Depth Over Time")
    fig.update_layout(xaxis_title="Time", yaxis_title="Depth (cm)")

    max_depth = df_filtered["depth"].max()
    min_depth = df_filtered["depth"].min()

    return fig, f"🔼 Max Depth: {max_depth} cm", f"🔽 Min Depth: {min_depth} cm"


@app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    Input("time-range", "value"),
    prevent_initial_call=True
)
def download_csv(n_clicks, range_value):
    df = fetch_data()
    df_filtered = filter_data(df, range_value)
    return dcc.send_data_frame(df_filtered.to_csv, "lake_depth_report.csv")


