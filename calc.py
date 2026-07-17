# ask the user for input

userx = int(input("What's x? "))

usery = int(input("What's y? "))

op = input("What's the operator? ").strip()


# do the actual math

if op == "+":
    print(f"Result is: {userx + usery}")

elif op == "-":
    print(f"The result is: {userx - usery}")

elif op == "*":
    print(f"The result is: {userx * usery}")

elif usery == 0:
    print("You can't divide 0 by 0") # BINGO!!

else:
    print(f"The result is: {userx / usery}")
