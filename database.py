from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///./sensor_data.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with tables!")

if __name__ == "__main__":
    init_db()


# init_db()
