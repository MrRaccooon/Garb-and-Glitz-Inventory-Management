from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

url = "postgresql://inventory:password@localhost:5432/inventory_db"
print("Testing DB URL:", url)
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        # use text(...) with SQLAlchemy 2
        r = conn.execute(text("SELECT version()"))
        print("Postgres version:", r.scalar())
    print("DB connection test: SUCCESS")
except SQLAlchemyError as e:
    print("DB connection test: FAILED")
    print(e)
