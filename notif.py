import datetime

import os

from dotenv import load_dotenv

import requests

from plyer import notification

from faker import Faker

import random



# auto find and load the .env file in this dir
load_dotenv()


fake = Faker()

# assign the real strings to the variables
city = "London"
addr = fake.address()
country = fake.country()
land = fake.location_on_land()

# the greeting numbers to us with the random module


base_url = "https://api.openweathermap.org/data/2.5/weather"
auth = os.getenv("WEATHER_API_KEY")


complete_url = f"{base_url}?q={city}&appid={auth}&units=metric"

response = requests.get(complete_url)
data = response.json()

temp = data['main']['temp'] # look at the parsed data so as to know WHY

desc = data['weather'][0]['description']


# get the current hour (24hr clock format)
current_hour = datetime.datetime.now().hour

weather = data

# the logic
if current_hour < 12:
    morning_options = [
        f"{temp}°C with {desc} in {city}. Early bird catces the worm as they say sir🎩",
        f"Slept well Master James?",
        f"A cup of coffee for the morning sir?"
    ]
    title_text="Good Morning Sir"
    message_text=random.choice(morning_options)
    app_name_text="Alfred"




elif current_hour < 18:
    afternoon_options = [
        f"{temp}°C with {desc} in {city}. Perfect time for a good stretch sir?",
        f"It's {temp}°C outside. Perhaps a glass of water is in order Master James?",
        f"The readings right now, {temp}°C with {desc} fancy a cup of evening tea sir",

    ]
    title_text="Evening Sir"
    message_text=random.choice(afternoon_options)
    app_name_text="Afternoon Alfred"



else:
    night_options = [
        f"{temp}°C with {desc}. A perfect way to end the night sir",
        f"{temp}°C with {desc} is today's final chapter sir🎩",
        "Fancy seeing you later Master James"
    ]
    title_text="Good Night Master James"
    message_text=random.choice(night_options)
    app_name_text="Night Alfred"



# the..store the reminders logic (we'll use file I/O)

# the time stamp we want to make

timestamp = datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S %p")

# first we ALWAYS open the file so as to know if it exists
with open("logs.txt", "r") as file:
    file.read() # just purely to read whats there



# now we WRITE(there's nothing in there so...not..logical appending) into the file
with open("logs.txt", "a") as file:
    file.write(f"[{timestamp}] [{title_text}] Reminded Master James: {message_text} | Weather: {temp}°C ({desc}) \n\n")


# Now call/send the notificaitons
#
#

if notification is not None: # trying to reassure BasedPytrigh ik and confirmed my sys has D-Bus
    notification.notify(
        title=title_text,
        message=message_text,
        app_name=app_name_text,
        app_icon="/home/bond/Pictures/Icons/cosmos_9147073.jpeg",
        timeout=5
    )
