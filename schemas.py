from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema for incoming sensor data (from ESP32)
class SensorDataCreate(BaseModel):
    sensor_id: int
    point_id: int
    depth: float
    timestamp: Optional[datetime] = None  # Auto-filled if not provided
    battery: Optional[float] = None
    rain: Optional[bool] = None
    max_level: Optional[bool] = None

# Schema for responses when fetching stored data
class SensorDataResponse(BaseModel):
    id: int
    sensor_id: int
    point_id: int
    depth: float
    timestamp: datetime
    battery: Optional[float] = None
    rain: Optional[bool] = None
    max_level: Optional[bool] = None

    class Config:
        from_attributes = True  # Allows ORM (SQLAlchemy) models to be converted to schemas

