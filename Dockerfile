# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt --prefer-binary

# Copy the rest of the application code into the container
COPY . .

# Compile babel locale
RUN pybabel compile -d locale -f

# Command to run the application
CMD ["python", "/app/__main__.py"]
