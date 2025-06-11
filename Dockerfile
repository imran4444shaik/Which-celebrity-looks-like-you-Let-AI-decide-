# Use Python 3.7 base image
FROM python:3.7-slim

# Set working directory
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install system dependencies required for some Python packages (like opencv)
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install all dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port for Streamlit
EXPOSE 8501

# Run your app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
