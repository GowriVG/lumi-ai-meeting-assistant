import numpy as np
from services.embedding_service import get_embedding

# In-memory store (for demo; enterprise → Azure AI Search)
vector_store = {}

def chunk_text(text, chunk_size=300):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def store_embeddings(meeting_id: str, transcript: str):
    chunks = chunk_text(transcript)

    embeddings = []
    for chunk in chunks:
        emb = get_embedding(chunk)
        embeddings.append((chunk, emb))

    vector_store[meeting_id] = embeddings


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(meeting_id: str, question: str, top_k=3):
    if meeting_id not in vector_store:
        return []

    question_embedding = get_embedding(question)

    scored = []
    for chunk, emb in vector_store[meeting_id]:
        score = cosine_similarity(question_embedding, emb)
        scored.append((chunk, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [chunk for chunk, _ in scored[:top_k]]