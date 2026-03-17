from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///fastapi-and-databases/student.db"

engine = create_engine(DATABASE_URL,echo=True)