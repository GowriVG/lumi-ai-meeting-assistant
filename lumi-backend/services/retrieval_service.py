import numpy as np
from services.embedding_service import get_embedding
from logger import logger

# In-memory store (for demo; enterprise → Azure AI Search)
vector_store = {}

def chunk_text(text, chunk_size=300):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_embeddings_batch(chunks):
    return [get_embedding(chunk) for chunk in chunks]

def store_embeddings(meeting_id: str, transcript: str):
    logger.info(f"Generating embeddings for meeting: {meeting_id}")
    chunks = chunk_text(transcript)

    embeddings = get_embeddings_batch(chunks)

    vector_store[meeting_id] = list(zip(chunks, embeddings))
    logger.info(f"Stored {len(chunks)} chunks for meeting: {meeting_id}")


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(meeting_id: str, question: str, top_k=5):
    logger.info(f"Retrieving chunks for question: {question}")

    if meeting_id not in vector_store:
        return []

    question_embedding = get_embedding(question)

    scored = []

    for chunk, emb in vector_store[meeting_id]:
        score = cosine_similarity(question_embedding, emb)
        scored.append((chunk, score))  # ✅ always append

    # Sort by relevance
    scored.sort(key=lambda x: x[1], reverse=True)

    # Optional threshold (safe)
    filtered = [chunk for chunk, score in scored if score > 0.5]

    # Fallback if nothing passes threshold
    if not filtered:
        filtered = [chunk for chunk, _ in scored[:top_k]]
    
    logger.info(f"Top {top_k} chunks retrieved for meeting: {meeting_id}")
    return filtered[:top_k]