# Base image - tried a few others, this one was the easiest and most resilient
FROM python:3.9.16-slim-buster

# Specify root directory in image
WORKDIR /app/dash

# Installing python requirements
COPY assets/GBADs_Documentation/small_requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt --no-cache-dir

# Copy dash files to image
COPY . /app/dash

# Specifying the dashboard command
CMD ["waitress-serve","--host=0.0.0.0","--port=80","--call","gbadsDash:returnApp"]