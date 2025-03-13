from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "postgresql://neondb_owner:npg_iso3LamnjO7k@ep-raspy-union-a8p6zewc-pooler.eastus2.azure.neon.tech/ES_db?sslmode=require"
# DATABASE_URL = "postgresql://neondb_owner:npg_iso3LamnjO7k@ep-raspy-union-a8p6zewc-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
# DATABASE_URL = "sqlite:///sensor_data.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the tables in the database
def init_db():
    print("🔄 Initializing database...")
    if not engine.dialect.has_table(engine.connect(), "sensor_data"):
        Base.metadata.create_all(bind=engine)  # ✅ Prevents re-running if table exists
        print("✅ Database initialized with tables!")
    else:
        print("⚠️ Database already initialized. Skipping...")


# if __name__ == "__main__":
#     init_db()


# init_db()
