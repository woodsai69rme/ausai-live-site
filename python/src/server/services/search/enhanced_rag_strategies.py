"""
Enhanced RAG Strategies - 2026 Update

Additional RAG techniques for improved document understanding:
- Multi-scale chunking
- Query transformation (HyDE, rewrite)
- Parent document retrieval
- Context compression
"""

import os
from typing import Any

from ...config.logfire_config import get_logger

try:
    from importlib.util import find_spec
    CROSSENCODER_AVAILABLE = find_spec("sentence_transformers") is not None
except ImportError:
    CROSSENCODER_AVAILABLE = False

logger = get_logger(__name__)


class QueryTransformer:
    """Transform queries for better RAG retrieval."""

    @staticmethod
    async def hyde_transform(query: str, llm) -> str:
        """HyDE: Generate hypothetical document before retrieval."""
        prompt = f"""Generate a hypothetical document that would perfectly answer this question.

Question: {query}

Hypothetical document:"""
        result = await llm.invoke(prompt)
        return str(result) if result is not None else ""

    @staticmethod
    async def rewrite_query(query: str, llm) -> str:
        """Rewrite query to be more searchable."""
        prompt = f"""Rewrite this search query to be more specific and search-friendly:

Original: {query}
Rewritten:"""
        result = await llm.invoke(prompt)
        return str(result) if result is not None else ""

    @staticmethod
    async def generate_multi_queries(query: str, llm) -> list[str]:
        """Generate multiple search perspectives."""
        prompt = f"""Generate 3 different search queries that would help find information about:

{query}

Queries:
1."""
        response = await llm.invoke(prompt)
        return [line.strip().lstrip("123.") for line in str(response).split("\n") if line.strip()][:3]


class MultiScaleChunker:
    """Index documents at multiple chunk sizes for better recall."""

    CHUNK_SIZES = [100, 200, 500, 1000]  # Tokens

    def __init__(self, text_splitter):
        self.text_splitter = text_splitter

    def create_multi_scale_index(
        self, documents: list[Any], vector_db
    ) -> dict[str, Any]:
        """Index same documents at multiple chunk sizes."""
        indexes_created = []

        for size in self.CHUNK_SIZES:
            # Adjust splitter for this chunk size
            self.text_splitter.chunk_size = size
            chunks = self.text_splitter.split_documents(documents)

            # Create index
            index_name = f"chunks_{size}"
            vector_db.create_index(index_name, chunks)
            indexes_created.append(index_name)

        return {"indexes": indexes_created, "chunk_sizes": self.CHUNK_SIZES}

    async def multi_scale_retrieve(
        self,
        query: str,
        query_embedding: list[float],
        vector_db,
        indexes: list[str],
        top_k: int = 10
    ) -> list[dict[str, Any]]:
        """Retrieve from all scales and merge with RRF."""
        all_results = []

        for index_name in indexes:
            results = await vector_db.similarity_search(
                query_embedding, k=top_k * 2, index=index_name
            )
            all_results.append(results)

        # Reciprocal Rank Fusion
        return self._reciprocal_rank_fusion(all_results, top_k)

    def _reciprocal_rank_fusion(
        self, result_lists: list[list[dict]], top_k: int
    ) -> list[dict[str, Any]]:
        """Merge multiple result lists using RRF algorithm."""
        scores: dict[str, float] = {}

        for results in result_lists:
            for rank, result in enumerate(results):
                doc_id = result.get("id")
                if doc_id:
                    # RRF formula: 1 / (rank + k) where k=60 typically
                    scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)

        # Sort by RRF score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        # Flatten all results to find matching doc
        all_results_flat = [r for results in result_lists for r in results]
        return [next(r for r in all_results_flat if r.get("id") == doc_id)
                for doc_id in sorted_ids[:top_k] if doc_id]


class ParentDocumentRetriever:
    """Retrieve small chunks but return larger parent context."""

    def __init__(self, vector_db, chunk_store, parent_store):
        self.vector_db = vector_db
        self.chunk_store = chunk_store
        self.parent_store = parent_store

    async def retrieve(
        self,
        query_embedding: list[float],
        child_splitter,
        parent_splitter,
        k: int = 10
    ) -> list[dict[str, Any]]:
        """Retrieve child chunks, return parent documents."""
        # Get child chunks via vector search
        child_chunks = await self.vector_db.similarity_search(
            query_embedding, k=k * 2
        )

        # Collect unique parents
        parent_ids = set()
        for chunk in child_chunks:
            parent_id = chunk.get("parent_id")
            if parent_id:
                parent_ids.add(parent_id)

        # Return parent documents with context from children
        parents = []
        for pid in list(parent_ids)[:k]:
            parent = self.parent_store.get(pid)
            if parent:
                parent["child_chunks"] = [
                    c for c in child_chunks if c.get("parent_id") == pid
                ]
                parents.append(parent)

        return parents


class ContextualCompressionRetriever:
    """Compress retrieved context for better LLM consumption."""

    def __init__(self, base_retriever, compressor_llm, max_tokens: int = 2000):
        self.base_retriever = base_retriever
        self.llm = compressor_llm
        self.max_tokens = max_tokens

    async def retrieve(self, query: str, k: int = 10) -> str:
        """Retrieve and compress to fit context window."""
        docs = await self.base_retriever.get_relevant_documents(query, k=k * 2)

        combined = "\n\n".join(d.page_content for d in docs)

        if len(combined.split()) > self.max_tokens:
            prompt = f"""Compress the following context to be most relevant to: {query}

Context:
{combined}

Compressed (keep key information only):"""
            compressed = await self.llm.invoke(prompt)
            return str(compressed) if compressed else combined

        return combined


# Configuration for enhanced strategies
ENHANCED_RAG_SETTINGS = {
    "hyde_enabled": os.getenv("USE_HYDE", "false").lower() == "true",
    "query_rewrite_enabled": os.getenv("USE_QUERY_REWRITE", "false").lower() == "true",
    "multi_scale_enabled": os.getenv("USE_MULTI_SCALE", "false").lower() == "true",
    "parent_doc_enabled": os.getenv("USE_PARENT_DOCS", "false").lower() == "true",
    "compression_enabled": os.getenv("USE_COMPRESSION", "false").lower() == "true",
    # Enhanced reranker options
    "reranking_model": os.getenv("RERANKING_MODEL", "BAAI/bge-reranker-large"),
    # Groq integration
    "use_groq": os.getenv("USE_GROQ", "false").lower() == "true",
    "groq_api_key": os.getenv("GROQ_API_KEY", ""),
}


def get_enhanced_settings() -> dict[str, Any]:
    """Get configuration for enhanced RAG features."""
    return ENHANCED_RAG_SETTINGS.copy()
