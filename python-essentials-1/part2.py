try:
    first_name=input("Enter your first name:")
    last_name=input("Enter your last name:")
    age=int(input("Enter your age:"))
    if age<0:
        print("Age cannot be negative")
    else:
        print("Full Name:-",first_name,last_name)
        print("You will be",age+1,"next year")
except ValueError:
    print("Invalid age input")