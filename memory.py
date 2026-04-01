import os
import pickle
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "google/embeddinggemma-300m"
SIMILARITY_THRESHOLD = 0.85

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(_BASE_DIR, "memory.index")
DATA_FILE = os.path.join(_BASE_DIR, "memory.pkl")

print(f"[memory] Loading semantic memory module from {_BASE_DIR}")
print(f"[memory] Using model: {MODEL_NAME}")

_model = SentenceTransformer(MODEL_NAME)
_dimension = _model.get_sentence_embedding_dimension()
_lock = threading.Lock()


def _new_index():
    return faiss.IndexFlatIP(_dimension)


def _load_state():
    if os.path.exists(INDEX_FILE) and os.path.exists(DATA_FILE):
        try:
            loaded_index = faiss.read_index(INDEX_FILE)
            with open(DATA_FILE, "rb") as f:
                loaded_store = pickle.load(f)

            if not isinstance(loaded_store, list):
                raise ValueError("memory store is not a list")

            print(
                f"[memory] Loaded existing memory: {loaded_index.ntotal} vectors, "
                f"{len(loaded_store)} records"
            )
            return loaded_index, loaded_store
        except Exception as exc:
            print(f"[memory] Failed to load persisted state, rebuilding empty index: {exc}")

    print("[memory] No persisted memory found, creating a new semantic index")
    return _new_index(), []


_index, _memory_store = _load_state()


def _save_state():
    faiss.write_index(_index, INDEX_FILE)
    with open(DATA_FILE, "wb") as f:
        pickle.dump(_memory_store, f)
    print(
        f"[memory] Saved memory state: {_index.ntotal} vectors -> "
        f"{os.path.basename(INDEX_FILE)}, {os.path.basename(DATA_FILE)}"
    )


if not os.path.exists(INDEX_FILE) or not os.path.exists(DATA_FILE):
    print("[memory] Persistence files missing; creating fresh memory.index and memory.pkl")
    _save_state()


def _embed_text(text):
    embedding = _model.encode([text], normalize_embeddings=True)
    return np.asarray(embedding, dtype=np.float32)


def search_memory(query, threshold=SIMILARITY_THRESHOLD):
    query = (query or "").strip()
    if not query:
        return None

    with _lock:
        if _index.ntotal == 0:
            print("[memory] search_memory skipped: index is empty")
            return None

        query_vector = _embed_text(query)
        scores, indices = _index.search(query_vector, 1)

        similarity = float(scores[0][0])
        top_idx = int(indices[0][0])

        print(f"[memory] Search top similarity={similarity:.4f}, threshold={threshold:.2f}")

        if similarity > threshold and 0 <= top_idx < len(_memory_store):
            matched_question, matched_answer = _memory_store[top_idx]
            print(f"[memory] HIT for query: {query!r} -> matched: {matched_question!r}")
            return matched_answer

    print(f"[memory] MISS for query: {query!r}")
    return None


def add_memory(question, answer):
    question = (question or "").strip()
    answer = (answer or "").strip()

    if not question or not answer:
        print("[memory] add_memory skipped: empty question or answer")
        return False

    with _lock:
        vector = _embed_text(question)
        _index.add(vector)
        _memory_store.append((question, answer))
        _save_state()

    print(f"[memory] Added memory entry. Total entries: {len(_memory_store)}")
    return True
