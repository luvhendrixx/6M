# 1. Install a lightweight Python environment
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy just the requirements file first (Great for Docker caching)
COPY requirements.txt .

# 4. Install the Python dependencies inside the container environment
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your local app files into the container
COPY . .

# 6. Open up the port that Uvicorn will listen on (change ports if there's confilcits)
EXPOSE 8000

# 7. The execution command when the container boots up (rm the ussd bit if you don't want that one and select your own..app or so and also..tweak the docker file to match your preferences as well)
CMD ["uvicorn", "ussd:app", "--host", "0.0.0.0", "--port", "8000"]

# 8. once your done, build the image using..
# docker build -t anker .  <- NOTE, -t tags the image with a friendly name of your choice..in this case...anker(make sure the name is in lowercase) and . meanss inside this current dir

# 9. run the container using ...
# docker run -d -p 8000:8000 --env-file .env --name ussd-container my-ussd-app   <- -d for detach mode(so it runs in the background), -p for port mapping HOST:CONTAINER always --env-file .env to auto inject your env varibles like your secrets in .env
