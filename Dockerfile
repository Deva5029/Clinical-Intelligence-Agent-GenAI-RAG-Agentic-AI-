# Use a slim Python image
FROM python:3.10-slim

# Install System Dependencies (Java 21 is the current standard for this image)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Java home for Spark (Updated path for Java 21)
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# Expose FastAPI port
EXPOSE 8000

# Start the API
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]