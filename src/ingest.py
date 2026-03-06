import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def ingest_data():
    client = QdrantClient(host="localhost", port=6333)
    embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    request_options={"timeout": 120}  # Adds a 2-minute buffer for slow connections
)

    # 1. Load the Parquet data created by PySpark
    df = pd.read_parquet("data/processed_trials.parquet")
    
    # 2. Create Collection in Qdrant
    client.recreate_collection(
        collection_name="clinical_trials",
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
    )

    # 3. Embed and Upload
    points = []
    for i, row in df.iterrows():
        # Combine title and summary for better search
        text_to_embed = f"{row['title']} {row['summary_clean']}"
        vector = embeddings.embed_query(text_to_embed)
        
        points.append(PointStruct(
            id=i,
            vector=vector,
            payload={"nct_id": row['id'], "text": text_to_embed}
        ))
    
    client.upsert(collection_name="clinical_trials", points=points)
    print("✅ Data successfully ingested into Qdrant!")

if __name__ == "__main__":
    ingest_data()