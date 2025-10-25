import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# load backend/.env if present
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(env_path, override=False)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://inventory:password@localhost:5432/inventory_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 20)),
    echo=(os.getenv("DB_ECHO", "False") == "True"),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as e:
        print("Error initializing DB:", e)
        raise

def drop_db():
    try:
        Base.metadata.drop_all(bind=engine)
    except SQLAlchemyError as e:
        print("Error dropping DB:", e)
        raise
