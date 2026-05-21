"""
embedder.py
-----------
Converts text chunks into vectors and stores them in ChromaDB.
Each chunk is tagged with project_id, phase_id, and source so
queries can be filtered to a specific project.
"""

from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer

from construct_iq.config import CHROMA_DIR, EMBEDDING_MODEL, TOP_K_RESULTS

_model: SentenceTransformer | None = None
_client: chromadb.PersistentClient | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def _collection():
    return _get_client().get_or_create_collection("construct_iq")


def index_chunks(
    chunks: list[str],
    project_id: int,
    phase_id: int,
    phase_name: str,
    source: str,
) -> None:
    """
    Embed and store text chunks in ChromaDB.
    source is the filename or 'note' — shown to the user as the citation.
    """
    if not chunks:
        return

    model      = _get_model()
    collection = _collection()
    embeddings = model.encode(chunks).tolist()

    ids = [f"{project_id}_{phase_id}_{source}_{i}" for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[
            {
                "project_id": project_id,
                "phase_id":   phase_id,
                "phase_name": phase_name,
                "source":     source,
            }
            for _ in chunks
        ],
    )


def delete_source(project_id: int, phase_id: int, source: str) -> None:
    """Remove all chunks for a given source (document or note)."""
    collection = _collection()
    results = collection.get(
        where={"$and": [{"project_id": project_id}, {"phase_id": phase_id}, {"source": source}]}
    )
    if results["ids"]:
        collection.delete(ids=results["ids"])


def query(text: str, project_id: int, n_results: int = TOP_K_RESULTS) -> list[dict]:
    """
    Find the most relevant chunks for a query within a project.
    Returns list of {text, phase_name, source} dicts.
    """
    model      = _get_model()
    collection = _collection()
    embedding  = model.encode([text]).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=n_results,
        where={"project_id": project_id},
    )

    chunks = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "text":       doc,
            "phase_name": meta["phase_name"],
            "source":     meta["source"],
        })
    return chunks
