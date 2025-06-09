from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import base64
import os

# Import your functions
from rag_engine import answer_question  # update this if you named it differently

app = FastAPI()

class QueryPayload(BaseModel):
    question: str
    image: Optional[str] = None  # base64 image, if any

@app.post("/api/")
async def get_answer(payload: QueryPayload):
    try:
        response = answer_question(payload.question)
        return response
    except Exception as e:
        return {"error": str(e)}

