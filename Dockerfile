# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt requirements.txt
COPY test_requirements.txt test_requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r test_requirements.txt

# Copy the rest of the application code to /app
COPY . .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app/src"


# Set the default command to run when the container starts
ENTRYPOINT ["python", "src/selenium_page_stubber/cli.py"]
