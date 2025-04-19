from sqlalchemy import Column, Integer, Float, DateTime, Boolean  
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# Database Model for Sensor Data
class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    point_id = Column(Integer, nullable=False) 
    depth = Column(Float, nullable=False)
    battery = Column(Float, nullable=False)
    rain = Column(Boolean, nullable=False)
    max_level = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
