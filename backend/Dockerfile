# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn
RUN pip install --no-cache-dir gunicorn

# Cloud Run requires the container to listen on port 8080
EXPOSE 8080
ENV PORT=8080

# Run Gunicorn as the WSGI server, binding to port 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "240", "app:app"]
