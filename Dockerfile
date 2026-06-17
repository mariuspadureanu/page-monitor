# IBM Page Monitor - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install --with-deps chromium

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY all-offerings-pages.xlsx .

# Create directories for data and logs
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Bucharest

# Run the application
CMD ["python", "src/main.py", "--schedule"]

# Made with Bob
