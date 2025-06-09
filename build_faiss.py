import faiss
import json
import pickle
import numpy as np

# Load embeddings
with open("embeddings.json", "r") as f:
    data = json.load(f)

# Prepare data for FAISS
texts = [item["text"] for item in data]
vectors = np.array([item["embedding"] for item in data]).astype("float32")

# Build FAISS index
dimension = len(vectors[0])
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

# Save index
faiss.write_index(index, "faiss_index.index")

# Save texts for reference
with open("texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print(f"✅ FAISS index built and saved with {len(texts)} documents.")

