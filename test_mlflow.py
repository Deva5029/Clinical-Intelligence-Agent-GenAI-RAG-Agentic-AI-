# Save this as test_mlflow.py and run it: python3 test_mlflow.py
import mlflow
import os
from dotenv import load_dotenv

load_dotenv()
mlflow.set_tracking_uri("http://localhost:5050")

try:
    with mlflow.start_run(run_name="Connection_Test"):
        mlflow.log_param("status", "working")
        print("✅ Success! Check MLflow UI now.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")