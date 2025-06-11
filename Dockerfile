# Use official Python 3.10 image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install critical packages first in correct order
RUN pip install --upgrade pip && \
    pip install protobuf==3.19.6 numpy==1.23.5 h5py==3.7.0 && \
    pip install typing-extensions==4.3.0 referencing==0.28.1 jsonschema==4.17.3 && \
    pip install keras==2.6.0  # Must be installed before tensorflow
    
# Install Python dependencies
COPY requirements.txt .
RUN #pip install tensorflow==2.15.0 && \
    pip install -r requirements.txt

# Copy project files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
