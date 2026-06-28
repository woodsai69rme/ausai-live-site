# Complete Documentation - Archon AI Document Understanding

**Date:** June 17, 2026
**Status:** Implementation Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Files Created/Modified](#files-createdmodified)
3. [Quick Start Guide](#quick-start-guide)
4. [Configuration](#configuration)
5. [API Reference](#api-reference)
6. [Architecture](#architecture)
7. [Model Recommendations](#model-recommendations)
8. [Advanced Features](#advanced-features)

---

## Overview

Archon is a production-ready RAG (Retrieval Augmented Generation) system for document understanding. It supports:

- Multiple cloud APIs (Gemini 2.5 Pro, GPT-4.1, Claude 4, DeepSeek)
- Local models via Ollama (Llama 4 Scout, Qwen 2.5 Coder)
- Advanced RAG strategies (HyDE, reranking, hybrid search)
- Document processing with Docling for PDF/table extraction

---

## Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `ARCHON_CODEBASE_REVIEW.md` | Full codebase analysis and recommendations |
| `python/src/server/services/search/enhanced_rag_strategies.py` | HyDE, multi-scale chunking, parent docs, compression |
| `DOCUMENTATION_COMPLETE.md` | This file |

### Modified Files

| File | Changes |
|------|---------|
| `AI-Models-Complete-Guide-2026-FULL.md` | Updated to 2026 model names |
| `AI-Models-Complete-Guide-2026.md` | Updated to 2026 model names |
| `python/src/server/utils/document_processing.py` | Added Docling PDF extraction |
| `python/src/server/services/search/rag_service.py` | Added `search_with_hyde()` method |
| `python/src/server/services/search/__init__.py` | Export enhanced strategies |
| `python/src/server/utils/__init__.py` | Export document processing functions |

---

## Quick Start Guide

### 1. Install Dependencies

```bash
cd C:\Users\karma\python
uv sync
uv pip install docling sentence-transformers
```

### 2. Enable Features

Create `.env` with:
```bash
USE_HYDE=true
USE_RERANKING=true
USE_AGENTIC_RAG=true
USE_CONTEXTUAL=true
SUPABASE_URL=your-url
SUPABASE_SERVICE_KEY=your-key
OPENROUTER_API_KEY=your-key
```

### 3. Run Server

```bash
uv run python -m src.server.main
# API at http://localhost:8181
```

### 4. Upload Documents

```bash
# Via API
curl -X POST http://localhost:8181/api/documents/upload \
  -F "file=@document.pdf"
```

---

## Configuration

### RAG Strategy Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `USE_HYDE` | false | Hypothetical Document Embeddings - generates fake answer before searching |
| `USE_RERANKING` | false | Re-scores results using CrossEncoder |
| `USE_AGENTIC_RAG` | false | Code-aware search with language detection |
| `USE_HYBRID_SEARCH` | false | Combines vector + keyword search |
| `USE_CONTEXTUAL` | false | Wraps chunks with surrounding context |
| `USE_GROQ` | false | Use Groq API for fast inference |

### Model Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `RERANKING_MODEL` | `BAAI/bge-reranker-large` | CrossEncoder model for reranking |
| `EMBEDDING_BATCH_SIZE` | 100 | Batch size for embedding creation |
| `DOCUMENT_STORAGE_BATCH_SIZE` | 50 | Batch size for storage |

---

## API Reference

### RAG Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/rag/query` | POST | Semantic search with all enabled strategies |
| `/api/rag/code-examples` | POST | Code-specific search |
| `/api/rag/sources` | GET | List available sources |
| `/api/documents/upload` | POST | Upload PDF/DOCX/TXT files |
| `/api/knowledge-items/crawl` | POST | Crawl URL and index content |

### Request Format

```json
{
  "query": "search text",
  "source": "optional-filter",
  "match_count": 5
}
```

### Response Format

```json
{
  "success": true,
  "results": [
    {
      "id": "result-id",
      "content": "document chunk",
      "metadata": {},
      "similarity_score": 0.85,
      "rerank_score": 0.92 (if reranking enabled)
    }
  ],
  "hyde_applied": true,
  "search_mode": "hybrid"
}
```

---

## Architecture

```
python/src/server/
├── api_routes/knowledge_api.py     # Document upload, crawling, search
├── services/
│   ├── embeddings/
│   │   └── embedding_service.py    # OpenAI/OpenRouter embeddings
│   ├── search/
│   │   ├── rag_service.py         # Main coordinator
│   │   ├── base_search_strategy.py # Vector similarity
│   │   ├── hybrid_search_strategy.py # Vector + keyword
│   │   ├── reranking_strategy.py  # CrossEncoder reranking
│   │   ├── agentic_rag_strategy.py # Code-aware search
│   │   └── enhanced_rag_strategies.py # HyDE, multi-scale, parent docs
│   └── storage/
│       └── document_storage_service.py # Batch storage
└── utils/
    └── document_processing.py     # PDF/DOCX/TXT extraction
```

---

## Model Recommendations

### By Use Case

| Use Case | Best Cloud | Best Local | VRAM Required |
|----------|------------|----------|---------------|
| Codebases | GPT-4.1-preview | Llama 4 Scout | 10GB (Q4) |
| Research | Gemini 2.5 Pro | Qwen 2.5 Coder 32B | 20GB |
| Code Search | Claude Code CLI | R1-Distill-32B | 20GB |
| Chat History | DeepSeek R1 | Llama 4 Scout | 10GB |
| Budget | DeepSeek (free) | Qwen 2.5 7B | 5GB |

---

## Advanced Features

### HyDE Query Transformation

```python
# Instead of searching with original query
# Generates hypothetical answer for better retrieval
from src.server.services.search import RAGService

rag = RAGService()
success, result = await rag.search_with_hyde("How does authentication work?")
```

### Multi-Scale Chunking

Index documents at 100, 200, 500, 1000 token chunks, retrieve with RRF fusion.

### Parent Document Retrieval

Retrieve small chunks but return larger parent context for better coherence.

### Contextual Compression

Compress retrieved context to fit LLM context window while preserving relevance.

---

**End of Documentation**

For questions: See inline code comments or ARCHON_CODEBASE_REVIEW.md