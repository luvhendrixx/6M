import random

from pydantic import BaseModel, computed_field

from fastapi import FastAPI, HTTPException

import json

import asyncio

import os

from dotenv import load_dotenv

from fastapi.security import APIKeyHeader

from fastapi import Depends # import fastapi security tools called Depends(Dependancies)

from typing_extensions import Optional



app = FastAPI(title="ussd")

load_dotenv()

dev_key = os.getenv("DEV_API_KEY")

# create the "db"
try:
    with open("ussd.json", "r") as file:
         ussd_db = json.load(file)

except FileNotFoundError:
    ussd_db = []

except json.JSONDecodeError:
    ussd_db = []


# define the machine blueprint for universal access
class USSD(BaseModel):
    title: str
    used: bool = False
    digit_length: int

    @computed_field
    def generated_code(self) -> int:
        start = 10**(self.digit_length - 1)
        end = (10** self.digit_length - 1)
        return random.randint(start, end)


# NOW we build the actual machine from our blueprints
def ussd_gen(length_input: int):
    new_ussd = USSD(title="USSD", digit_length=length_input)

    # turn the NEW USSD blueprint into a dict we can actually store
    return new_ussd.model_dump()

# start the timer loop (pressing the button/turning on the machine)
async def background_ussd_worker():
    global ussd_db
    interval = 10.0

    while True: # keep doing this forever while the server is alive
        fresh_code_dict = ussd_gen(5) # stamp a fresh code(the computed field handles the math)

        ussd_db.append(fresh_code_dict) # add it to the "db" list

        # save the file
        with open("ussd.json", "w") as file:
            json.dump(ussd_db, file, indent=4)

        # take a non-blocking 10s nap (lets fastapi handle traffic)
        await asyncio.sleep(interval)

# create the endpoints that listens for calls to the endpoints
@app.post("/redeem/{code}")
def validate_ussd(code: str): # incase a user tries to be funny, let them in first then block em...just for fun

    # check if the string consists of ints/numbers
    if not code.isdigit(): # a buit-in string method that returns True is all chars are digits 0-9 and false if there are letters/symbols
        return {"status": f"Yo bro🫪, {code} is not a number"} # consisentency in naming for..easier json parsing incase you intergrate this to a frontend

    # if its a number, convert it to an int for the db for loop
    int_code = int(code)

    for every_code in ussd_db:
        if every_code["generated_code"] == int_code:
            # don't exit yet but check if its status == true
            if every_code["used"]: # i excluded == True cause...here is just like saying True == True..which is just redundancy
                return {"status": "WHOA!!", "details": f"your code: {code} has already been used", "reaction": "🫢"}

            else:
                # change the flag to true
                every_code["used"] = True

            # now open the "db" and save
            with open("ussd.json", "w") as file:
                json.dump(ussd_db, file, indent=4)

            # Instead of: return f"Your code: {code} has been redeemed successfully👀🍸"
            # We do this so we avoid that weird % and having to key in -w "\n" everytime...means write new line btw:
            return {"status": "success", "message": f"Code {code} redeemed successfully", "icon": "👀🍸"}

    raise HTTPException(status_code=404, detail="Um...that's not one of ours🫪")


# now we make a GET endpoint for the dev using their API key
# 1. Tell FastAPI to look for a header named "x-api-key"
api_header = APIKeyHeader(name="key")

# 2. now we make the logic to check the key
def verify_dev_key(incoming_key: str = Depends(api_header)):
    if incoming_key != dev_key:
        raise HTTPException(status_code=403, detail="Invalid API Key 😂🫵")
    return incoming_key

# 3. if the API key checks out..then list all codes
@app.get("/codes", dependencies=[Depends(verify_dev_key)])
def list_all_codes(status: Optional[str] = None): # default without flags means, you see everything
    with open("ussd.json", "r") as file:
        all_codes = json.load(file)

    # if you don't pass a status/query per se...you see everything
    if status is None:
        return all_codes

    # if you asked for used codes
    if status == "used":
        return [code for code in all_codes if code["used"] is True]

    # if you asked for un-used codes
    elif status == "unused":
        return [code for code in all_codes if code["used"] is False]

    # error checking if your weird and keyed in banana💀
    else:
        raise HTTPException(status_code=400, detail=f"{status} is not a flag😂🫵")
