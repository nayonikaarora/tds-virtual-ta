import os
import faiss
import json
import pickle
import requests
import numpy as np
from typing import List, Dict
from bs4 import BeautifulSoup

# Load env
#AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMxMDAwMDkwQGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.KQrHjqysfOPIAYpcJJlCJZcZelUrpmDfFfdbcZsPIQg"
EMBEDDING_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"
LLM_ENDPOINT = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

# Load FAISS index and texts
index = faiss.read_index("faiss_index.index")
with open("texts.pkl", "rb") as f:
    texts = pickle.load(f)

def embed_text(text: str) -> List[float]:
    print(AIPROXY_TOKEN)
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "text-embedding-3-small",
        "input": text
    }
    response = requests.post(EMBEDDING_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def retrieve_similar_chunks(question: str, k: int = 5) -> List[str]:
    query_vector = np.array(embed_text(question)).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vector, k)
    return [texts[i] for i in indices[0]]

def generate_answer_with_context(question: str, context_chunks: List[str]) -> Dict:
    context_text = "\n\n".join(context_chunks[:5])
    messages = [
        {"role": "system", "content": "You are a helpful teaching assistant for the Tools in Data Science course. Use the provided context to answer the student's question."},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"}
    ]
    headers = {
        "Authorization": f"Bearer {AIPROXY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.4
    }
    print("Payload:", json.dumps(payload, indent=2))

    response = requests.post(LLM_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    answer = response.json()["choices"][0]["message"]["content"]
return {
    "answer": answer,
    "links": [{"url": "https://example.com", "text": "example snippet"}]
}


def answer_question(question: str) -> Dict:
    try:
        context = retrieve_similar_chunks(question)
        return generate_answer_with_context(question, context)
    except Exception as e:
        return {"error": str(e)}

