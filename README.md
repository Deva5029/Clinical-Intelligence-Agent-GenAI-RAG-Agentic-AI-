Implemented the full lifecycle: from raw data engineering with Spark to a reasoning agent powered by LangGraph and Gemini.

Step 1: Data Engineering & ETL (The Spark Pipeline)
You started with raw clinical data (like the dataset.csv you provided). In pipeline.py, you used PySpark to clean and structure this data.

What happened: The script reads the CSV, handles missing values (like Other Outcome Measures), and creates a unified "text" column that combines the Study Title, Conditions, and Interventions.

Result: A clean .parquet file in your data/ folder, optimized for fast reading.

Step 2: Vector Ingestion (The Search Engine)
Standard databases can’t "understand" medical context, so you built a Vector Database.

The Model: You used gemini-embedding-001 to turn clinical summaries into 3,072-dimensional vectors.

The Database: You deployed Qdrant in a Docker container.

What happened: ingest.py reads the Parquet data, creates embeddings, and stores them in Qdrant. Now, if you search for "heart attack," the system knows to look for "myonecrosis" because they are mathematically close in vector space.

Step 3: The Intelligence Layer (LangGraph & Gemini)
Instead of a simple chatbot, you built a Stateful Agent in agent.py using LangGraph.

The Workflow: You defined a graph with two nodes:

Retrieve Node: This node takes your question, converts it to a vector, and queries Qdrant for the top 3 most relevant clinical trials.

Reason Node: This node passes the retrieved trial data and your question to gemini-2.0-flash.

The Constraint: You programmed the agent to answer only based on the provided context, preventing "hallucinations" (making up medical facts).

Step 4: API & Infrastructure (FastAPI & Docker)
To make this useful for a user, you wrapped the agent in a web service.

FastAPI: In main.py, you created an /ask endpoint. When a user sends a query, it triggers the LangGraph workflow and returns the answer.

Docker Compose: You used Docker to orchestrate your infrastructure, ensuring that Qdrant and MLflow start with the exact same configuration every time.

Step 5: Observability & Tracking (MLflow)
Because medical AI requires strict monitoring, you integrated MLflow.

Tracking: Every time someone asks a question, the agent logs:

The model used (gemini-2.0-flash).

The specific question asked.

Metrics: The latency_sec (how many seconds it took the agent to think).

Audit Trail: You can see exactly what context was retrieved from the database to justify the agent's answer.

Step 6: Orchestration (The Run Script)
Finally, you created run.sh, a master control script that automates the deployment:

Clears blocked ports (like 5050 and 8000).

Starts the Docker containers.

Activates your Python virtual environment.

Launches the FastAPI server.

Summary of the Tech Stack
Language: Python (Data Science & Backend)

AI Models: Google Gemini (Inference & Embeddings)

Big Data: PySpark (Cleaning)

Vector DB: Qdrant (Retrieval)

Orchestration: LangGraph (Reasoning Flow)

DevOps: Docker & Docker Compose

MLOps: MLflow (Monitoring)
