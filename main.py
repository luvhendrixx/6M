import os

import httpx

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Query

import getpass

from pydantic import BaseModel

import json



# load the key
load_dotenv()



# initialise the application
app = FastAPI(title="Alfred API")


username = getpass.getuser().capitalize()
# get pass used to get current logged in user, but doesn't work here since we're working with...HTTP client

# defining a GET endpoint at "/"(root)
@app.get("/")
def read_root():
    return {
        "status": "Online",
        "message": f"Guten Tag {username}"
    }


# define another endpoint
@app.get("/status")
def get_status():
    return {
        "cpu_status": "Cool",
        "butler_mood": "Fine sir",
        "tea_temp": "Fancy"
    }


# adding the weather endpoint
@app.get("/weather/{city}")
async def get_weather(city: str, units: str | None = Query(default="metric")):
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    auth = os.getenv("WEATHER_API_KEY")

    # error checking the .env with the API key
    if not auth:
        raise HTTPException(status_code=500, detail="Weather API key not configured")

    full_url = f"{base_url}?q={city}&appid={auth}&units={units}"


    # use httpx for async ops(operations)
    async with httpx.AsyncClient() as client:
        response = await client.get(full_url)

    # error checking the weather API response
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="City not found or API error")

    # add the return function so we see the weather API response & contents
    data = response.json()

    # in fastapi, you must always use return otherwise you endpoint will always be null

    # return clean formatted dict of our choice from the response we got
    return {
        "city": data['name'],
        "temp": data['main']['temp'],
        "description": data['weather'][0]['description'],
        "units": "Celsius" if units == "metric" else "Farenheit"
    }


# onto POST API's

# defining what a task MUST contian
class Task(BaseModel):
    title: str
    priority: str = "medium" # default to medium if not specified
    details: str | None = None # optional extra deets

# create a temp "db" to hold tasks while the server is running
#tasks_db = [] -> for temp testing (was living in RAM)


# making the "db" persistent (we LOAD && READ first)
try:
    with open("tasks.json", "r") as file:
        tasks_db = json.load(file) # this is just for parsing(making things into small chunks so as to easily read it)

except FileNotFoundError:
    tasks_db = []

except json.JSONDecodeError:
    tasks_db = []


# create the POST endpoints -> receive and add to the "db"
@app.post("/tasks")
def add_task(new_task: Task):
    # turn the pydantic object into a std dict
    tasks_db.append(new_task.dict()) # in the .dict, you can also use .model_dump() as well

    with open("tasks.json", "w") as file:
        json.dump(tasks_db, file, indent=4)


    return {
        "message": f"Task received and filed {username}",
        "added task": new_task
    }



# a GET endpoint to actually see the tasks we added (POSTED)
@app.get("/tasks")
def view_tasks():
    return {
        "todo_list": tasks_db,
        "total_tasks": len(tasks_db)
    }
