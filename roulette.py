import random

import time

import sys

# define what's there
chambers = ["A", "B", "C"]

# prompt the user for input
user_choice = input("Your turn: A, B or C? ").strip().upper()

# set the conditions
if user_choice not in chambers:
    print("Man up yo🫩")
    sys.exit(1)

else:
    print("\nLoading the machine...")
    time.sleep(1.0)
    print("*spins the chambers...")
    time.sleep(1.5)
    print("Now...*Pulls the trigger*")

# the random bullet
bullet = random.choice(chambers)

# the outcome
if user_choice == bullet:
    print(f"Welp...👉🏻👆🏼💥")

else:
    print("Lucky bastard💀")
