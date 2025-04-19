from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema for incoming sensor data (from ESP32)
class SensorDataCreate(BaseModel):
    sensor_id: int
    point_id: int
    depth: float
    battery: Optional[float] = None
    rain: Optional[bool] = None
    max_level: Optional[bool] = None
    timestamp: Optional[datetime] = None  # Auto-filled if not provided

# Schema for responses when fetching stored data
class SensorDataResponse(BaseModel):
    id: int
    sensor_id: int
    point_id: int
    depth: float
    battery: float
    rain: bool
    max_level: bool
    timestamp: datetime

    class Config:
        from_attributes = True  # Allows ORM (SQLAlchemy) models to be converted to schemas

