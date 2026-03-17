from db import engine
from table import students
from sqlalchemy import insert,select,update,delete


def create_students(input_name:str,input_age:int,input_city:str):
    with engine.connect() as conn:
        check_query = select(students).where(students.c.name == input_name)
        existing = conn.execute(check_query).fetchone()
        
        if existing:
            print(f"Student '{input_name}' already exists. Skipping insertion.")
            return

        query = insert(students).values(name=input_name,age=input_age,city=input_city)
        conn.execute(query)
        conn.commit()
        print("User created successfully")

def get_students():
    with engine.connect() as conn:
        query = select(students)
        result = conn.execute(query)
        return result.fetchall()

def update_student(name:str,age:int,city:str):
    with engine.connect() as conn:
        query = update(students).where(students.c.name==name).values(age=age,city=city)
        conn.execute(query)
        conn.commit()
        print("User updated successfully")

def delete_student():
    with engine.connect() as conn:
        query = delete(students).where(students.c.age<18)
        conn.execute(query)
        conn.commit()
        print("User deleted successfully")