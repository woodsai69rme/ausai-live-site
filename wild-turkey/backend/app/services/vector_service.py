"""Vector Database Service.

Initializes ChromaDB for semantic agent memory retrieval and document chunk ingestion.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False
    logger.warning("chromadb not installed, vector service running in fallback mode.")

CHROMA_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")

_chroma_client = None
_memory_collection = None

if _CHROMA_AVAILABLE:
    try:
        os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_DATA_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        _memory_collection = _chroma_client.get_or_create_collection(
            name="wild_turkey_memory",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("ChromaDB vector service initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        _chroma_client = None
        _memory_collection = None


def upsert_vector_memory(entry_id: str, document: str, metadata: dict[str, Any]) -> None:
    """Upsert a memory entry into the vector database."""
    if not _memory_collection:
        logger.warning("Vector DB unavailable, skipping memory upsert.")
        return
        
    try:
        _memory_collection.upsert(
            documents=[document],
            metadatas=[metadata],
            ids=[entry_id]
        )
    except Exception as e:
        logger.error(f"Vector DB upsert failed: {e}")


def search_vector_memory(query: str, n_results: int = 10, filter_metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Search for semantic memory matches."""
    if not _memory_collection:
        logger.warning("Vector DB unavailable, returning empty search results.")
        return []
        
    try:
        results = _memory_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        formatted_results = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "distance": results["distances"][0][i] if results.get("distances") else 0.0
                })
        return formatted_results
    except Exception as e:
        logger.error(f"Vector DB search failed: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Lightweight text chunker for RAG document splitting."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            break_point = text.rfind('\n', start, end)
            if break_point == -1 or break_point < start + (chunk_size // 2):
                break_point = text.rfind(' ', start, end)
            if break_point != -1 and break_point > start:
                end = break_point
        chunks.append(text[start:end].strip())
        start = end - overlap if end < len(text) else len(text)
    return [c for c in chunks if c]


def ingest_file(file_path: str, user_id: str) -> int:
    """Read a local file, chunk it, and ingest into Vector DB."""
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return 0
        
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        chunks = chunk_text(content)
        file_name = os.path.basename(file_path)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"file-{file_name}-{i}-{int(os.path.getmtime(file_path))}"
            meta = {
                "user_id": str(user_id),
                "category": "file_ingestion",
                "title": f"{file_name} (Part {i+1})",
                "source_file": file_path,
                "chunk_index": i
            }
            upsert_vector_memory(chunk_id, chunk, meta)
            
        logger.info(f"Ingested {len(chunks)} chunks from {file_name}")
        return len(chunks)
    except Exception as e:
        logger.error(f"Failed to ingest file {file_path}: {e}")
        return 0


def ingest_directory(directory_path: str, user_id: str, extensions: list[str] = [".md", ".py", ".ts", ".txt"]) -> dict[str, int]:
    """Scan a directory and ingest supported files into Vector DB."""
    stats = {"files_processed": 0, "chunks_ingested": 0}
    
    if not os.path.isdir(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return stats
        
    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = os.path.join(root, file)
                chunks = ingest_file(full_path, user_id)
                if chunks > 0:
                    stats["files_processed"] += 1
                    stats["chunks_ingested"] += chunks
                    
    logger.info(f"Directory ingestion complete: {stats['files_processed']} files, {stats['chunks_ingested']} chunks.")
    return stats
