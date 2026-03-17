from db import engine
from sqlalchemy import MetaData,Table,Column,Integer,String

metadata = MetaData()

students=Table(
    "students",
    metadata,
    Column("id",Integer,primary_key=True),
    Column("name",String,nullable=False),
    Column("age",Integer),
    Column("city",String,nullable=True)
)


def create_tables():
    metadata.create_all(engine)
    print("Tables created successfully")