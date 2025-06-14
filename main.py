from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from rag_engine import answer_question

app = FastAPI()

# Enable CORS (Allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to the deployment domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    question: str
    image: Optional[str] = None

@app.post("/api/")
async def get_answer(payload: QueryPayload):
    try:
        response = answer_question(payload.question, payload.image)
        return response
    except Exception as e:
        return {"error": str(e)}
