# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (build-essential for Python libs, texlive for CV generation)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    git \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Use Gunicorn as the production server (Reduced workers for Render Free tier memory limits)
CMD ["sh", "-c", "gunicorn -w 1 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:$PORT --timeout 120"]
