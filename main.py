from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import database, models, schemas, crud
import json

app = FastAPI()

# Initialize the database
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
                "depth": db_data.depth,
                "timestamp": db_data.timestamp.isoformat()
            }))
        except WebSocketDisconnect:
            disconnected_clients.append(connection)

    # Remove disconnected clients
    for connection in disconnected_clients:
        active_connections.remove(connection)

    return db_data

@app.get("/sensor_data/{point_id}", response_model=list[schemas.SensorDataResponse])
def get_sensor_data(point_id: int, limit: int = 10, db: Session = Depends(database.get_db)):
    """Fetches the latest sensor data for a given point"""
    return crud.get_sensor_data(db, point_id, limit)
