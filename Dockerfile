FROM node:18-alpine AS node-base

COPY ["package-lock.json", "package.json", "./"]
RUN npm install

FROM python:3.12-slim-bullseye AS python-base

COPY ["pyproject.toml", "poetry.lock", "./"]
RUN pip install poetry==1.8.3
RUN poetry install
RUN python -m spacy download en_core_web_sm

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

COPY data.json /app/

COPY /scripts/deploy.sh /app/deploy.sh
RUN chmod +x /app/deploy.sh

# Expose the port the app runs on
EXPOSE 8000

# Run the deployment script and then start the Django server
ENTRYPOINT ["/app/deploy.sh"]
