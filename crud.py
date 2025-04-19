from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

# Function to insert sensor data
def create_sensor_data(db: Session, data: schemas.SensorDataCreate):
    db_data = models.SensorData(
        sensor_id=data.sensor_id,
        point_id=data.point_id,
        depth=data.depth,
        battery=data.battery,
        rain=data.rain,
        max_level=data.max_level,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(db_data)
    db.commit()
    # db.close()
    db.refresh(db_data)
    return db_data

# Function to retrieve sensor data with an optional limit
def get_sensor_data(db: Session, sensor_id: int):
    query = db.query(models.SensorData).filter(models.SensorData.sensor_id == sensor_id)
    return query.all()
