# rag_engine.py
import os
import faiss
import pickle
import numpy as np
import requests
from typing import List
import base64
from PIL import Image
import pytesseract
import io

# Load FAISS index and metadata
index = faiss.read_index("faiss_index.index")
with open("metadata.pkl", "rb") as f:
    metadata = pickle.load(f)

# AI Proxy setup
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZHMxMDAwMDkwQGRzLnN0dWR5LmlpdG0uYWMuaW4ifQ.KQrHjqysfOPIAYpcJJlCJZcZelUrpmDfFfdbcZsPIQg"
AI_PROXY_BASE = "https://aiproxy.sanand.workers.dev/openai/v1"
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

HEADERS = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json"
}

# Helper: get embedding from AI Proxy
def get_embedding(text: str) -> List[float]:
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }
    response = requests.post(f"{AI_PROXY_BASE}/embeddings", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Embedding error: {response.status_code} - {response.text}")

# Helper: OCR from image
def extract_text_from_image(image_base64: str) -> str:
    try:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        print(f"⚠️ Error processing image: {e}")
        return ""

# Helper: search FAISS index
def search_similar_docs(query: str, k: int = 5):
    query_vector = np.array([get_embedding(query)]).astype("float32")
    D, I = index.search(query_vector, k)
    results = [metadata[i] for i in I[0] if i < len(metadata)]
    return results

# Helper: generate answer from AI Proxy Chat API
def generate_answer(question: str, context: str):
    prompt = f"""
You are a helpful TA for a data science course. Use the context to answer the question concisely and clearly.

Context:
{context}

Question:
{question}

Answer:
"""
    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    response = requests.post(f"{AI_PROXY_BASE}/chat/completions", headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"Completion error: {response.status_code} - {response.text}")

# Main RAG function
def answer_question(question: str, image: str = None):
    if image:
        extracted_text = extract_text_from_image(image)
        if extracted_text:
            question += f"\n\nAlso consider this image content:\n{extracted_text}"

    retrieved_docs = search_similar_docs(question)
    context = "\n".join([doc["text"] for doc in retrieved_docs])
    links = [{"url": doc["url"], "text": doc["text"][:200]} for doc in retrieved_docs]
    answer = generate_answer(question, context)
    return {"answer": answer, "links": links}
