# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
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

# Download NLTK data (if used)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"

# Download SpaCy model (if used)
# This model is a common default; adjust if your application uses a different one
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the application using Gunicorn
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:$PORT"]
