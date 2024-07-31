FROM python:3.12.2-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .
# RUN COMMAND AND MAKE SURE IT IS AVAILABLE EXTERNALLY
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
