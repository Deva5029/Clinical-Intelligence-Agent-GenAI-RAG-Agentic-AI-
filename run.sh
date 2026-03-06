#!/bin/bash

# 1. Clean up any "ghost" processes on Port 8000 and 5000
echo "🧹 Cleaning up ports..."
kill -9 $(lsof -t -i:8000) 2>/dev/null
# Note: If MLflow is on 5000, we let Docker handle it, but we clear 8000 for FastAPI

# 2. Activate Virtual Environment
echo "🐍 Activating Virtual Environment..."
source venv/bin/activate

# 3. Set Python Path (Crucial for finding the 'src' folder)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 4. Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please open Docker Desktop."
    exit 1
fi

# 5. Start Infrastructure ONLY (Qdrant & MLflow)
# We exclude 'app' here so we can run it locally for faster debugging
echo "🐳 Spinning up Infrastructure (Qdrant, MLflow)..."
docker-compose up -d qdrant mlflow

# 6. Wait for Qdrant to be ready (Health check)
echo "⏳ Waiting for Vector DB to stabilize..."
sleep 5

# 7. Check if processed data exists; if not, run the pipeline
if [ ! -d "data/processed_trials.parquet" ]; then
    echo "📥 First-time setup: Running Spark ETL and Ingestion..."
    ./venv/bin/python src/pipeline.py
    ./venv/bin/python src/ingest.py
fi

# 8. Launch the FastAPI App locally
echo "🚀 Launching Clinical Intelligence API at http://localhost:8000/docs"
./venv/bin/python -m src.main