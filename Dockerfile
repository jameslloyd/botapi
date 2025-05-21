# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.10-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file into the container at /app
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which can reduce image size.
# --trusted-host pypi.python.org: Sometimes necessary if there are SSL/TLS issues with PyPI.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# 5. Copy the rest of the application code into the container at /app
COPY . .

# 6. Expose the port the app runs on
# This should match the port Uvicorn/Gunicorn is configured to use.
EXPOSE $PORT

# 7. Define the command to run the application
# For Cloud Run, it's common to use Gunicorn as the ASGI server.
# Uvicorn can also be used directly with its Gunicorn-compatible worker class.
# The --host 0.0.0.0 makes the app accessible from outside the container.
# The --port $PORT allows Cloud Run to inject the port it wants the container to listen on.
# If $PORT is not set, it defaults to 8000.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:${PORT}"]

# Alternatively, for simpler local testing or if you prefer uvicorn directly:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# However, for Cloud Run, the Gunicorn command above is more robust.
