from fastapi import FastAPI
from src.agent import clinical_agent
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Clinical Trial Intel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Platform is Online"}

@app.post("/ask")
async def ask_clinical_question(query: str):
    # This invokes the LangGraph agent
    inputs = {"question": query}
    result = clinical_agent.invoke(inputs)
    return {"answer": result["answer"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)