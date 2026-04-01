print("memory.py loaded successfully")
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
MODEL_NAME = "google/embeddinggemma-300m"

model = SentenceTransformer(MODEL_NAME)

INDEX_FILE = "memory.index"
DATA_FILE = "memory.pkl"

dimension = 768

if os.path.exists(INDEX_FILE):

    index = faiss.read_index(INDEX_FILE)

    with open(DATA_FILE, "rb") as f:
        memory_store = pickle.load(f)

else:

    index = faiss.IndexFlatIP(dimension)
    memory_store = []


def save_memory():

    faiss.write_index(index, INDEX_FILE)

    with open(DATA_FILE, "wb") as f:
        pickle.dump(memory_store, f)


def add_memory(question, answer):

    print("Saving memory entry...")

    vector = model.encode(
        [question],
        normalize_embeddings=True
    )

    index.add(np.array(vector))

    memory_store.append((question, answer))

    save_memory()


def search_memory(query, threshold=0.70):

    if index.ntotal == 0:
        return None

    query_vector = model.encode(
        [query],
        normalize_embeddings=True
    )

    scores, indices = index.search(query_vector, 1)

    similarity = scores[0][0]

    if similarity > threshold:

        return memory_store[indices[0][0]][1]

    return None