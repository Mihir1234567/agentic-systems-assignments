from table import create_tables
from crud_ops import create_students,get_students,update_student,delete_student

create_tables()
create_students("Mihir",15,"Ahmedabad")
create_students("Rahul",19,"Mumbai")
create_students("Amit",21,"Bangalore")

# print(get_students())

update_student("Rahul",200,"Surat")

delete_student()

print(get_students())


