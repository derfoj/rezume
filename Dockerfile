# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV WEB_CONCURRENCY=1
# Default to dev, can be overridden to 'prod' in docker-compose or render
ENV ENV_STATE=dev 

# Set the working directory
WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure necessary directories exist
RUN mkdir -p outputs/generated_cvs data/img/uploads

# Persistence Note: 
# To persist the database, mount a volume to /app/data or use a Postgres URL.
# Example: docker run -v ./data:/app/data -e DATABASE_URL=sqlite:////app/data/rezume.db ...

# Expose port (Render standard)
EXPOSE 10000

# Start command: Single worker, high timeout for AI stability
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "api:app", "--bind", "0.0.0.0:10000", "--timeout", "120"]
