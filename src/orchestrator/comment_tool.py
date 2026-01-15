from __future__ import annotations

import os
from typing import Any, Dict, List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from .state_types import TopologyState
from ..config import get_settings
from ..dependencies import get_session_maker
from ..db import vector_client


async def _get_embedding_from_ollama(text: str, model: str, api_base: str) -> List[float]:
    """
    Get embedding from Ollama using direct HTTP API call.
    
    This avoids the LangChain OpenAI wrapper which tokenizes the input,
    causing 'invalid input type' errors with Ollama's embedding endpoint.
    """
    url = f"{api_base}/embeddings"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={
                "model": model,
                "input": text,  # Raw text string, not tokens
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract embedding from response
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["embedding"]
        elif "embedding" in data:
            return data["embedding"]
        else:
            raise ValueError(f"Unexpected embedding response format: {data}")


async def run_comment_tool(state: TopologyState) -> Dict[str, Any]:
    """
    Query pgvector for user comments / tickets relevant to this query.

    Flow:
      - Build a search query text from user_input (and possibly ui_context).
      - Embed that text using the configured embedding backend.
      - Use pgvector (via vector_client.search_comment_embeddings) to find
        the top-K most similar comments.
      - Return a structured payload suitable for the orchestrator and UI.

    Assumes a Postgres table `comment_embeddings` with columns:
      - comment_id (text)
      - embedding (vector)
      - metadata (jsonb)
    and that it is populated by an offline ingestion process.
    """
    settings = get_settings()

    user_input: str = state.get("user_input", "") or ""
    ui_context: Dict[str, Any] = state.get("ui_context", {}) or {}

    # print(f"DEBUG: comment_tool input='{user_input}'")

    if not user_input.strip():
        print("DEBUG: comment_tool skipping due to empty input")
        return {
            "comments": [],
            "metadata": {
                "source": "comment_tool",
                "reason": "empty user_input",
            },
        }

    # --- 1) Build the semantic search text -------------------------------

    # Simple strategy: just use the user_input for now.
    # Later you can augment with site IDs, layer, etc.
    search_text = user_input

    # --- 2) Embed the query ----------------------------------------------

    api_base = os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1")
    embedding_model = settings.embedding_model_name

    try:
        embedding: List[float] = await _get_embedding_from_ollama(
            text=search_text,
            model=embedding_model,
            api_base=api_base,
        )
    except Exception as exc:
        print(f"DEBUG: comment_tool embedding failed: {exc}")
        return {
            "comments": [],
            "metadata": {
                "source": "comment_tool",
                "reason": f"embedding_failed: {exc}",
            },
        }

    # --- 3) Search pgvector ----------------------------------------------

    SessionLocal = get_session_maker()
    async with SessionLocal() as session:  # type: AsyncSession
        rows = await vector_client.search_comment_embeddings(
            session,
            embedding=embedding,
            limit=settings.comment_rag_top_k,
        )
        print(f"DEBUG: comment_tool db search returned {len(rows)} rows")

    # rows: [ {comment_id, embedding, metadata, distance}, ... ]
    comments: List[Dict[str, Any]] = []
    for row in rows:
        metadata = row.get("metadata") or {}
        comments.append(
            {
                "comment_id": row.get("comment_id"),
                "distance": float(row.get("distance", 0.0)),
                # Merge metadata fields directly for convenience in the UI.
                **metadata,
            }
        )

    # print(f"DEBUG: comment_tool comments={comments}")

    return {
        "comments": comments,
        "metadata": {
            "source": "comment_rag_pgvector",
            "query_text": search_text,
            "top_k": settings.comment_rag_top_k,
            "num_results": len(comments),
        },
    }
