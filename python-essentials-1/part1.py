try:
    num1 = int(input("Enter a number: "))
    num2 = int(input("Enter a number: "))
    print("The Sum is", num1+num2)
    print("The Division is", num1/num2)
except ValueError:
    print("Invalid input")
except ZeroDivisionError:
    print("Cannot divide by zero")