import faiss
import json
import pickle
import numpy as np

# Load embeddings
with open("embeddings.json", "r") as f:
    data = json.load(f)

# Prepare data for FAISS
vectors = np.array([item["embedding"] for item in data]).astype("float32")

# Save metadata (text + url)
metadata = [{"text": item["text"], "url": item["url"]} for item in data]

# Build FAISS index
dimension = len(vectors[0])
index = faiss.IndexFlatL2(dimension)
index.add(vectors)

# Save index
faiss.write_index(index, "faiss_index.index")

# Save metadata for reference
with open("metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ FAISS index built and saved with {len(metadata)} documents.")
