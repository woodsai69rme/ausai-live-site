# Archon Knowledge Engine - Codebase Review & Enhancement Guide

**Review Date:** June 17, 2026  
**System Version:** 0.1.0  

---

## Executive Summary

Archon implements a **production-ready RAG system** with sophisticated search strategies. The architecture follows clean separation of concerns with dedicated services for each component.

### Strengths
- Multi-strategy RAG pipeline (vector → hybrid → reranking → agentic)
- Proper error handling that never corrupts data (skips on failure)
- WebSocket progress tracking for long operations
- Configurable strategies via credential service
- Contextual embeddings support
- Code-aware search with language/framework detection

### Opportunities for Enhancement
1. **Document Processing**: Add Docling for superior PDF/table extraction
2. **Query Transformation**: Implement HyDE and query rewriting
3. **Multi-Scale Chunking**: Index same doc at multiple chunk sizes
4. **Advanced Reranking**: Upgrade to BGE-reranker-large or ColBERT
5. **Performance**: Add Groq integration for faster inference

---

## Architecture Overview

```
archon-ui-main/              # React + TypeScript frontend (port 3737)
python/
├── src/server/
│   ├── main.py              # FastAPI app with 9 API routers
│   ├── socketio_app.py      # Socket.IO for real-time updates
│   │
│   ├── api_routes/
│   │   ├── knowledge_api.py # Main API endpoints for crawl/upload/search
│   │   └── settings_api.py
│   │
│   ├── services/
│   │   ├── embeddings/
│   │   │   ├── embedding_service.py   # OpenAI/OpenRouter embeddings with retry logic
│   │   │   └── contextual_embedding_service.py
│   │   │
│   │   ├── search/
│   │   │   ├── rag_service.py          # Coordinator + pipeline orchestration
│   │   │   ├── base_search_strategy.py # Vector similarity search
│   │   │   ├── hybrid_search_strategy.py # Vector + BM25 keyword search
│   │   │   ├── reranking_strategy.py   # CrossEncoder-based reranking
│   │   │   ├── agentic_rag_strategy.py # Code example search
│   │   │   └── keyword_extractor.py    # Query → keyword extraction
│   │   │
│   │   └── storage/
│   │       └── document_storage_service.py # Batch processing with progress
│   │
│   └── utils/
│       └── document_processing.py # PDF/DOCX/TXT extraction
```

---

## Search Strategy Pipeline

### 1. Base Vector Search (`base_search_strategy.py`)
- Uses Supabase `match_archon_crawled_pages` RPC
- Filters by similarity threshold (0.15)
- Foundation for all other strategies

### 2. Hybrid Search (`hybrid_search_strategy.py`)
- **Phase 1**: Vector search (semantic understanding)
- **Phase 2**: Keyword search (exact terms)
- **Phase 3**: Merge with priority ordering:
  - Hybrid matches (appears in both) → 20% score boost
  - Vector-only matches (semantic)
  - Keyword-only matches (exact terms)

### 3. Reranking (`reranking_strategy.py`)
- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (default)
- Re-scores results by query-document relevance
- Returns results sorted by `rerank_score`

### 4. Agentic RAG (`agentic_rag_strategy.py`)
- Detects code-related queries (languages, frameworks, APIs)
- Searches `archon_code_examples` table specifically
- Extracts code context (language, line numbers, file path)

---

## Key Services Analysis

### Embedding Service (`embedding_service.py`)
```python
# Key features:
- Batch processing with configurable size (default 100)
- Rate limiting via ThreadingService
- Retry logic (exponential backoff)
- Never stores empty/zero embeddings (ALPHA PRINCIPLE)
- Tracks failures in EmbeddingBatchResult
```

**Enhancement Opportunity**: Add support for alternative embedding models:
- `bge-large-en-v1.5` (better accuracy, local)
- `text-embedding-3-small` (cheaper for volume)

### Document Storage (`document_storage_service.py`)
```python
# Key features:
- Sequential batch processing
- Contextual embeddings integration
- Cancellation support
- Retry with exponential backoff
- Individual fallback on batch failure
```

### Keyword Extractor (`keyword_extractor.py`)
- Preserve list: `authentication`, `jwt`, `oauth`, `api`, etc.
- Filter list: `the`, `is`, `to`, `get`, `set`, etc.
- Build variations: singular/plural, -ing, -ed forms

---

## RAG Performance Recommendations

### For Large Codebases (Llama 4 Scout advantage)
The guide mentions Llama 4 Scout with **10M context window**. Archon currently works within context limits but could leverage this:

1. **Direct LLM Mode**: For codebases < 10M tokens, send entire code at once
2. **Current RAG limit**: ~8K chunks based on 1000-char chunks

### Query Enhancement Implementation

```python
# Add to hybrid_search_strategy.py
async def hyde_retrieve(self, query: str, llm, vector_db):
    """Generate hypothetical answer before retrieval."""
    prompt = f"Generate a hypothetical document that would answer: {query}"
    hypothetical = await llm.invoke(prompt)
    return await vector_db.similarity_search(hypothetical, k=5)

# Add to keyword_extractor.py
def rewrite_query(self, query: str, llm) -> str:
    """Transform query to be more search-friendly."""
    prompt = f"Rewrite for search: {query}\nPrecise search query:"
    return llm.invoke(prompt)
```

---

## Document Processing Enhancements

Current supports:
- ✅ PDF (PyPDF2, pdfplumber)
- ✅ DOCX (python-docx)
- ✅ TXT, MD, RST (UTF-8 decode)

Missing/advanced needs:
- ❌ **Docling** for layout-aware extraction (tables, figures)
- ❌ **Docx-inspect** for better table structure
- ❌ **OCR fallback** for scanned PDFs

### Docling Integration Example
```python
# Add to document_processing.py
try:
    from docling.document_converter import DocumentConverter
    DOCKING_AVAILABLE = True
except ImportError:
    DOCKING_AVAILABLE = False

def extract_text_from_pdf_enhanced(file_content: bytes) -> str:
    if not DOCKING_AVAILABLE:
        return extract_text_from_pdf(file_content)  # Fallback
    
    converter = DocumentConverter()
    result = converter.convert_stream(io.BytesIO(file_content))
    return result.document.export_to_markdown()
```

---

## Settings Configuration

Available via `credential_service`:
| Setting | Default | Purpose |
|---------|---------|---------|
| `USE_RERANKING` | false | Enable CrossEncoder reranking |
| `USE_HYBRID_SEARCH` | false | Combine vector + keyword |
| `USE_AGENTIC_RAG` | false | Enable code example extraction |
| `USE_CONTEXTUAL_EMBEDDINGS` | false | Wrap chunks with context |
| `EMBEDDING_BATCH_SIZE` | 100 | Batch size for embeddings |
| `DOCUMENT_STORAGE_BATCH_SIZE` | 50 | Batch size for storage |

---

## Testing Coverage

Test files found:
- `test_rag_strategies.py` - Strategy testing
- `test_rag_simple.py` - Basic RAG tests
- `test_embedding_service_no_zeros.py` - Zero embedding prevention
- `test_service_integration.py` - Integration tests
- `test_api_essentials.py` - API endpoint tests

---

## Immediate Action Items

### High Priority
1. **Add Docling integration** for PDF processing
2. **Implement query rewriting** in hybrid strategy
3. **Add multi-query generation** for broader recall
4. **Upgrade reranker to BGE-reranker-large**

### Medium Priority
5. **Add Groq API option** for fast inference
6. **Multi-scale chunking** implementation
7. **Parent document retriever** for better context

### Low Priority
8. **RAG evaluation metrics** (Ragas integration)
9. **Reciprocal rank fusion** for multi-scale results
10. **Contextual compression** for token efficiency

---

## Completed Enhancements (June 17, 2026)

### Document Processing
- ✅ Added Docling support with fallback chain (docling → pdfplumber → PyPDF2)
- ✅ Added `extract_document_structure()` for tables/figures
- ✅ Updated exports in `__init__.py`

### RAG Strategies
- ✅ Created `enhanced_rag_strategies.py` with:
  - `QueryTransformer` - HyDE, rewrite, multi-query
  - `MultiScaleChunker` - Multiple chunk sizes with RRF fusion
  - `ParentDocumentRetriever` - Child-to-parent retrieval
  - `ContextualCompressionRetriever` - Token-efficient compression
- ✅ Added `search_with_hyde()` to RAGService
- ✅ Updated search strategy exports

---

## Model Recommendations (2026)

| Use Case | Model | Context | VRAM | Notes |
|----------|-------|---------|------|-------|
| Code Understanding | GPT-4.1-preview | 128K | API | Agentic coding |
| Code Understanding | Qwen 2.5 Coder 32B | 32K | 20GB (Q4) | Best local text analysis |
| Large Codebases | Llama 4 Scout | 10M | 10GB (Q4) | Massive context window |
| Reasoning | DeepSeek R1 | 128K | 20GB (Q4) | Chain-of-thought |
| Fast Inference | Groq API | 8K | API | 500+ tokens/sec |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/knowledge-items/crawl` | POST | Crawl URL with progress |
| `/api/documents/upload` | POST | Upload PDF/DOCX/TXT |
| `/api/rag/query` | POST | Semantic search query |
| `/api/rag/code-examples` | POST | Code-specific search |
| `/api/knowledge-items/{id}` | DELETE | Remove source |
| `/api/knowledge-items/sources` | GET | List sources |
| `/health` | GET | Health check |

---

**License**: MIT (Archon), Educational (AI Models Guide)