# Use an official Python image as the base
FROM python:3.10-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y curl && apt-get clean

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH for all subsequent steps
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy the rest of the application files
COPY . .

# Copy the .env file into the container
COPY .env .env

# Expose the application port
EXPOSE 8000

# Command to start the FastAPI app using uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]