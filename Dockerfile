# Use the official Python image from the Docker Hub
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
# Install Poetry
RUN pip install poetry==1.8.3

COPY pyproject.toml poetry.lock /app/

RUN poetry install

COPY local /app/local

COPY prod /app/prod

COPY healthharmony /app/healthharmony

# Run Django migrations
RUN poetry run python -m healthharmony.manage migrate

# Expose the port the app runs on
EXPOSE 9000

RUN poetry run python -healthharmony.manage collectstatic

# Start the Django server
# CMD ["poetry", "run", "python3", "-m", "healthharmony.manage", "runserver", ":9000"]
# Set the entrypoint to ensure the specified command is always run
ENTRYPOINT ["poetry", "run", "daphne", "-p", "9000", "-b", "0.0.0.0", "healthharmony.app.asgi:application"]
