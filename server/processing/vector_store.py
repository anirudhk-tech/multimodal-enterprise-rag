import os
from typing import Any, Dict, List, Optional

from config import get_qdrant_client
from qdrant_client.http import models as qm

from processing.embeddings import embed_text

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "pokemon_corpus")
EMBED_DIM = 1536

import logging

logger = logging.getLogger(__name__)


def ensure_collection() -> None:
    client = get_qdrant_client()
    if COLLECTION_NAME in [c.name for c in client.get_collections().collections]:
        return
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=qm.VectorParams(
            size=EMBED_DIM,
            distance=qm.Distance.COSINE,
        ),
    )


def upsert_document(doc_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
    ensure_collection()
    client = get_qdrant_client()
    numeric_id = abs(hash(doc_id))
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            qm.PointStruct(
                id=numeric_id,
                vector=vector,
                payload=metadata,
            )
        ],
    )


def search_similar(
    query_vector: List[float],
    limit: int = 5,
    filters: Optional[qm.Filter] = None,
) -> List[Dict[str, Any]]:
    ensure_collection()
    client = get_qdrant_client()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        with_payload=True,
        limit=limit,
        query_filter=filters,
    )
    return [
        {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


def build_vector_context(message: str) -> Dict[str, Any]:
    vector_context_snippets = []

    try:
        q_vec = embed_text(message)
        hits = search_similar(q_vec, limit=3)

        for h in hits:
            payload = h["payload"] or {}
            snippet = payload.get("text") or ""
            if snippet:
                vector_context_snippets.append(snippet)
    except Exception:
        pass

    vector_context_str = "\n\n".join(vector_context_snippets)

    return {"context": vector_context_str}
