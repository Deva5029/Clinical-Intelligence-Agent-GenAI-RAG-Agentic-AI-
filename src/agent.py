import os
import time
import mlflow
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from qdrant_client import QdrantClient

# 1. Load environment variables FIRST
load_dotenv()

# 2. Configure MLflow Tracking
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5050")
mlflow.set_tracking_uri(MLFLOW_URI)

experiment_name = "clinical_trials_v1"
try:
    mlflow.set_experiment(experiment_name)
except Exception:
    mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)

# 3. Initialize Qdrant Client
# Ensure host matches your .env (usually 'localhost' for local run, 'qdrant' for docker)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
client = QdrantClient(host=QDRANT_HOST, port=6333)

# 4. Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    request_options={"timeout": 120}
)

# Define the State for LangGraph
class GraphState(TypedDict):
    question: str
    context: List[str]
    answer: str

# --- NODE 1: RETRIEVAL ---
def retrieve_data(state: GraphState):
    print("---SEARCHING VECTOR DATABASE---")
    query_vector = embeddings.embed_query(state["question"])
    
    try:
        search_result = client.query_points(
            collection_name="clinical_trials",
            query=query_vector,
            limit=3  # Increased to 3 for better context
        )
        
        context = [point.payload["text"] for point in search_result.points]
        
        if not context:
            context = ["No relevant clinical data found."]
            
    except Exception as e:
        print(f"Search failed: {e}")
        context = ["Error accessing the vector database."]
        
    return {"context": context}

# --- NODE 2: REASONING ---
def reason_and_answer(state: GraphState):
    print("---GEMINI IS REASONING---")
    
    start_time = time.time()
    model_name = "gemini-2.0-flash" # Updated to current flash model
    
    llm = ChatGoogleGenerativeAI(
        model=model_name, 
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0,
        max_retries=1
    )

    try:
        # Start a nested MLflow run to log this specific inference
        with mlflow.start_run(nested=True, run_name="Clinical_Inference"):
            system_msg = "You are a Clinical Trial Assistant. Answer based ONLY on the provided context. If the answer is not in the context, say you do not know."
            user_msg = f"Context: {' '.join(state['context'])}\n\nQuestion: {state['question']}"
            
            response = llm.invoke([
                {"role": "system", "content": system_msg},
                HumanMessage(content=user_msg)
            ])
            answer = response.content
            
            # LOGGING PARAMETERS & METRICS
            end_time = time.time()
            latency = end_time - start_time
            
            mlflow.log_param("model_used", model_name)
            mlflow.log_param("query", state["question"])
            mlflow.log_metric("latency_sec", latency)
            
    except Exception as e:
        print(f"Inference failed: {e}")
        if "429" in str(e):
            answer = "❌ Daily Quota Exceeded. Please check Google AI Studio billing/limits."
        else:
            answer = f"Error: {str(e)}"
            
    return {"answer": answer}

# --- BUILD THE GRAPH ---
workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_data)
workflow.add_node("reason", reason_and_answer)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reason")
workflow.add_edge("reason", END)

clinical_agent = workflow.compile()