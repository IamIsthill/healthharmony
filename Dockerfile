FROM python:3.12.2-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
COPY tailwind.config.js tailwind.config.js

RUN pip3 install -r requirements.txt