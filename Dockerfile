# Use the official Python image from the Docker Hub
FROM python:3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install pip requirements
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Copy the entire app directory to the container
COPY . .

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["uvicorn", "fastapi_tasks.main:app", "--host", "0.0.0.0", "--port", "8000"]