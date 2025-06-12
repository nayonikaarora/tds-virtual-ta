# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from rag_engine import answer_question

app = FastAPI()

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
