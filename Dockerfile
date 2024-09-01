FROM node:18-alpine AS node-base

COPY [ "package-lock.json", "package.json", "./"]

RUN npm install


FROM python:3.12-slim-bullseye AS python-base

COPY ["pyproject.toml", "poetry.lock", "./"]

RUN pip install poetry==1.8.3

RUN poetry install

WORKDIR /app

ENV PYTHONNONBUFFERED=1
ENV PYTHONPATH=.

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY local /app/local

COPY healthharmony /app/healthharmony

COPY .env /app/
COPY db.sqlite3 /app/
COPY node_modules /app/

# Run Django migrations
RUN poetry run python -m healthharmony.manage migrate



# Expose the port the app runs on
EXPOSE 8080

RUN poetry run python -m healthharmony.manage collectstatic --noinput

# Start the Django server
ENTRYPOINT ["poetry", "run", "daphne", "-p", "8080", "-b", "0.0.0.0", "healthharmony.app.asgi:application"]
