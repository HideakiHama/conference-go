# Select the base image that is best for our application
# Install any operating system junk
# Set the working directory to copy stuff to
# Copy all the code from the local directory into the image
# Install any language dependencies
# Set the command to run the application
FROM python:3

WORKDIR /app

COPY accounts accounts
COPY attendees attendees
COPY common common
COPY conference_go conference_go
COPY events events
COPY presentations presentations
COPY requirements.txt requirements.txt
COPY manage.py manage.py

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:8000 conference_go.wsgi