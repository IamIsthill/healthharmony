# Add the main parent layer
FROM python:3.10-slim-bullseye

WORKDIR /app

# Copy source code
COPY /healthharmony .
COPY /pyproject.toml .

# Install dependencies
RUN
