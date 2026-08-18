# Base Python Image
FROM python:3.12-slim

# Set Working Directory
WORKDIR /app

# Prevent Python from writing bytecode and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files
COPY . .

# Create Data Directory for Chroma Vector DB & SQLite Chat History
RUN mkdir -p /app/data

# Expose FastAPI (8000) and Streamlit (8501) ports
EXPOSE 8000
EXPOSE 8501

# Default Command (Runs FastAPI Backend)
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
