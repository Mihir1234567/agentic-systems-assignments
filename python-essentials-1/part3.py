try:
    name=input("Enter your name:")
    age=int(input("Enter your age:"))
    print("Hello",name)
    if age<0:
        print("Age cannot be negative")
    elif age<13:
        print("You are a child")
    elif age<18:
        print("You are a teenager")
    elif age<60:
        print("You are an adult")
    else:
        print("You are a senior citizen")
    if age>18:
        print("You are eligible for voting")
    else:
        print("You are not eligible for voting")
except ValueError:
    print("Invalid age input")