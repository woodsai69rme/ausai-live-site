# The Complete Guide to AI Models for Document Understanding & Reasoning

**Version 3.0 | February 2026 | The Definitive Reference**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [How AI Actually Understands Documents](#2-how-ai-actually-understands-documents)
3. [Cloud-Based Models](#3-cloud-based-models)
4. [Open-Source & Local Models](#4-open-source--local-models)
5. [Fast Inference APIs & Hosting](#5-fast-inference-apis--hosting)
6. [Hardware Requirements](#6-hardware-requirements)
7. [Semantic Search & RAG Systems](#7-semantic-search--rag-systems)
8. [Advanced RAG Techniques](#8-advanced-rag-techniques)
9. [Document Processing Tools](#9-document-processing-tools)
10. [Complete Comparison Tables](#10-complete-comparison-tables)
11. [Recommendations by Use Case](#11-recommendations-by-use-case)
12. [Quick Start Guides](#12-quick-start-guides)
13. [Code Examples](#13-code-examples)
14. [Resources & Links](#14-resources--links)
15. [Appendices](#appendices)

---

## 1. Introduction

### Why This Guide Exists

Most AI tools fail at actual document understanding. They perform keyword matching, not semantic reasoning. This guide covers **every model, tool, technique, and optimization** for systems that actually "read" and "understand" your documents.

### What You'll Learn

- The difference between keyword search vs semantic understanding
- **Every major AI model available in 2026** (cloud and local)
- Hardware requirements for running models locally
- How to build systems that actually understand context
- Advanced RAG techniques (chunking, reranking, query transformation)
- Document processing and parsing tools
- Fast inference APIs (Groq, etc.)
- Complete comparison tables for quick decisions
- Full code examples for every approach

### Who This Is For

- Developers analyzing codebases
- Researchers working with papers and documentation
- Anyone who needs AI to actually understand their files
- People frustrated with "stupid" keyword-based tools
- Teams building production RAG systems

### The Core Problem

**What "Stupid" Tools Do:**
```
User: "Find authentication code"
Stupid Tool: Searches for word "authentication"
Result: Misses login(), signin(), auth(), security checks
```

**What "Smart" Tools Do:**
```
User: "Find authentication code"
Smart Tool: Uses semantic embeddings
Result: Finds all authentication-related code regardless of naming
```

---

## 2. How AI Actually Understands Documents

### Three Pillars of Document Understanding

#### Pillar 1: Context Window

The amount of text a model can process in a single prompt.

| Context Size | Tokens | What It Fits |
|--------------|--------|--------------|
| Tiny | 4K | ~2 pages |
| Small | 32K | ~15 pages |
| Medium | 128K | ~60 pages, small codebase |
| Large | 200K | ~100 pages |
| XL | 1M | ~500 pages, entire book |
| XXL | 2M | ~1000 pages, large codebase |
| Massive | 10M | Massive codebases + history |

#### Pillar 2: Embeddings (Semantic Search)

Embeddings convert text into vectors (lists of numbers) that capture meaning.

```
"authentication" → [0.23, -0.45, 0.12, ...]
"login" → [0.21, -0.43, 0.15, ...]  (Similar!)
"banana" → [0.89, 0.12, -0.67, ...]  (Different!)
```

**Best Embedding Models:**

| Model | Dimensions | Type | Best For |
|-------|------------|------|----------|
| nomic-embed-text | 768 | Local | General purpose, fast |
| bge-large-en-v1.5 | 1024 | Local | High accuracy |
| bge-m3 | 1024 | Local | Multilingual |
| e5-large-v2 | 1024 | Local | Multilingual |
| OpenAI text-embedding-3-large | 3072 | Cloud | High quality |
| OpenAI text-embedding-3-small | 1536 | Cloud | Cost-effective |
| Cohere embed-v4 | 1024 | Cloud | Enterprise |
| Voyage-2 | 1024 | Cloud | Long context |
| Jina-embeddings-v3 | 1024 | Local/Cloud | Multilingual |

#### Pillar 3: Reasoning Capability

Some models just predict next tokens. Others actually "think."

**Models WITH Reasoning:**
- DeepSeek R1 (shows chain-of-thought)
- GPT-5 with thinking mode
- Claude with extended thinking
- OpenAI o1/o3 series

**Models WITHOUT Reasoning:**
- Standard GPT-4
- Gemini Flash
- Most smaller local models

### The RAG Pipeline

**Retrieval Augmented Generation** is how you handle documents larger than context window:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Documents  │ ──► │   Parsing    │ ──► │  Chunking   │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                    ┌──────────────┐            │
                    │   Embedding  │ ◄──────────┘
                    └──────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Vector DB  │
                    └─────────────┘
                           │
┌──────────────┐           │
│   Query      │           │
└──────────────┘           │
       │                   │
       ▼                   ▼
┌──────────────────────────────┐
│     Semantic Search          │
│  (Find relevant chunks)      │
└──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│     Reranking (Optional)     │
│  (Re-order by relevance)     │
└──────────────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│     LLM Generation           │
│  (Answer using context)      │
└──────────────────────────────┘
```

---

## 3. Cloud-Based Models

### 3.1 Google Gemini Family

#### Gemini 2.5 Pro (Latest - 2026)

| Specification | Value |
|---------------|-------|
| Context Window | **1M tokens** (~750K words) |
| Multimodal | Text, images, audio, video |
| Reasoning | Extended thinking mode |
| Training Data | Up to mid 2025 |
| Access | Google AI Studio, Vertex AI |

**Best For:**
- Processing entire codebases at once
- Analyzing multiple large documents
- Multimodal tasks (docs + images + video)
- Complex reasoning

**Pricing:**
| Tier | Input | Output |
|------|-------|--------|
| Standard | $1.25/1M tokens | $5.00/1M tokens |
| With context caching | $0.31/1M tokens | $5.00/1M tokens |

#### Gemini 2.0 Flash

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Speed | Very fast |
| Cost | $0.10/1M input, $0.40/1M output |

**Best For:**
- High-volume processing
- Quick document summaries
- Budget-conscious workloads

---

#### Gemini 2.5 Pro

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Video Processing | Up to 3 hours |
| Thinking Model | Yes, with extended reasoning |

---

#### Gemini 2.0 Flash

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Speed | Very fast |
| Cost | $0.10/1M input, $0.40/1M output |

**Best For:**
- High-volume processing
- Quick document summaries
- Batch processing many files

---

### 3.2 OpenAI GPT Family

#### GPT-4.1 (Current Flagship 2026)

| Specification | Value |
|---------------|-------|
| Context Window | 128K tokens |
| Thinking Mode | Built-in o1-style reasoning |
| Knowledge Cutoff | Mid 2025 |

**Pricing:** $2.50/1M input, $10.00/1M output

#### GPT-4.1-mini (Fast Budget Option)

Fastest GPT-4.1 variant for quick queries and high-volume chat.

#### GPT-4.1-preview (Code Specialist)
Optimized for code understanding and agentic coding tasks.

---

### 3.3 Anthropic Claude Family

#### Claude Opus 4

| Specification | Value |
|---------------|-------|
| Context Window | 200K tokens |
| Thinking | Extended thinking mode |
| Specialty | Complex analysis |

**Pricing:** $15.00/1M input, $75.00/1M output

---

#### Claude Sonnet 4

| Specification | Value |
|---------------|-------|
| Context Window | 200K tokens |
| Speed | 3x faster than Opus |
| Cost | 1/5 of Opus |

**Pricing:** $3.00/1M input, $15.00/1M output

---

#### Claude Code (CLI Tool)

Command-line tool for code understanding with direct file system access.

```bash
npm install -g @anthropic-ai/claude-code
claude --dir ./my-project
```

---

### 3.4 DeepSeek Family

#### DeepSeek V3.2 (Current Flagship)

| Specification | Value |
|---------------|-------|
| Parameters | 671B (MoE - only 37B active) |
| Context Window | 128K tokens |
| Performance | Matches GPT-5, Gemini 3 |
| License | MIT (fully open) |

**Pricing (API):** $0.14/1M input, $0.28/1M output

---

#### DeepSeek R1 (Reasoning Specialist)

Trained with pure reinforcement learning for chain-of-thought reasoning.

**Pricing (API):** $0.55/1M input, $2.19/1M output

---

#### DeepSeek R1 Distilled Models

| Model | Parameters | VRAM Needed (Q4) |
|-------|------------|------------------|
| R1-Distill-Qwen-1.5B | 1.5B | 1GB |
| R1-Distill-Qwen-7B | 7B | 4GB |
| R1-Distill-Qwen-14B | 14B | 8GB |
| R1-Distill-Qwen-32B | 32B | 18GB |
| R1-Distill-Llama-70B | 70B | 40GB |

---

### 3.5 Other Cloud Providers

| Provider | Model | Context | Best For |
|----------|-------|---------|----------|
| Mistral AI | Mistral Large 2 | 128K | General reasoning |
| Mistral AI | Codestral | 32K | Code generation |
| xAI | Grok 2 | 131K | Real-time info |
| Cohere | Command R+ | 128K | Enterprise RAG |
| Amazon | Bedrock | Varies | Multi-model access |

---

## 4. Open-Source & Local Models

### 4.1 Meta Llama 4 Family

#### Llama 4 Scout

| Specification | Value |
|---------------|-------|
| Context Window | **10M tokens** (~7.5M words) |
| Parameters | 17B (MoE, ~3B active) |
| License | Llama Community License |
| Multimodal | Yes |

**This is INSANE for local use.** 10M tokens means:
- Entire large codebases in one context
- Years of chat history in single prompt
- Complete documentation libraries together

**Hardware Requirements:**
| Quantization | VRAM |
|--------------|------|
| Q4_K_M | 10GB |
| Q8 | 18GB |
| FP16 | 34GB |

#### Llama 4 Maverick

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Parameters | 17B (MoE, ~3B active) |

#### Llama 4 Code

Specialized for code understanding and generation.

### 4.2 Qwen Family

#### Qwen3-Coder (2026)

| Specification | Value |
|---------------|-------|
| Parameters | 80B total, 3B active (MoE) |
| Context Window | **256K tokens** |
| License | Apache 2.0 |

**VRAM:** 5GB (Q4), 8GB (Q8)

#### Qwen 2.5 Coder 32B

| Specification | Value |
|---------------|-------|
| Parameters | 32B |
| Context Window | 32K tokens |

**VRAM:** 18-20GB (Q4)

### 4.3 DeepSeek Family (2026)

#### DeepSeek V3

| Specification | Value |
|---------------|-------|
| Parameters | 671B (MoE - only 37B active) |
| Context Window | 128K tokens |
| License | MIT (fully open) |

**Hardware to Run:**
- Requires 350GB+ VRAM (multi-GPU server)
- Use distilled versions for consumer hardware

#### DeepSeek R1

| Specification | Value |
|---------------|-------|
| Base | DeepSeek V3 |
| Specialty | Chain-of-thought reasoning |

**Pricing (API):** $0.55/1M input, $2.19/1M output (via DeepSeek)

---

### 4.3 Other Open Models

| Model | Params | Context | VRAM (Q4) | Best For |
|-------|--------|---------|-----------|----------|
| Mixtral 8x7B | 47B | 32K | 24GB | Efficient general |
| Mixtral 8x22B | 141B | 65K | 80GB | Large open model |
| Yi-1.5-34B | 34B | 32K | 18GB | General purpose |
| Phi-4 | 14B | 16K | 8GB | Small, reasoning |
| Gemma 2 27B | 27B | 8K | 16GB | General purpose |

---

## 5. Fast Inference APIs & Hosting

### 5.1 Groq (Fastest Inference 2026)

Groq provides the fastest inference using custom LPU chips.

**Speed:** Up to 625 tokens/second for Llama 4 Scout (free tier available)

**Available Models (2026):**
- Llama 4 Scout
- Llama 4 Maverick  
- Llama 3.3 70B
- Mixtral 8x7B
- Qwen 2.5 Coder

**Pricing:**
| Plan | Cost |
|------|------|
| Free | $0 (rate limited) |
| Developer | Pay per token |

**How to Use:**

```python
from groq import Groq

client = Groq(api_key="your-api-key")

completion = client.chat.completions.create(
    model="llama-4-scout-17b-16e-instruct",
    messages=[
        {"role": "user", "content": "Analyze this document..."}
    ],
)
```

**Groq vs Others:**
| Provider | Speed (tokens/sec) | Cost |
|----------|-------------------|------|
| Groq | 500-625 | Low |
| OpenAI | 50-100 | Medium |
| Anthropic | 30-60 | High |
| Local (RTX 4090) | 40-80 | Hardware cost |

---

### 5.2 Together AI

Hosted open-source models with good pricing.

**Available Models:**
- All major open models
- Fine-tuning support

---

### 5.3 Fireworks AI

Fast inference for open-source models.

---

### 5.4 OpenRouter

Unified API for all major models (cloud and open).

```python
import openai

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-api-key"
)

# Access any model
response = client.chat.completions.create(
    model="deepseek/deepseek-r1",
    messages=[{"role": "user", "content": "..."}]
)
```

---

### 5.5 Self-Hosting Options

| Tool | Best For | Difficulty |
|------|----------|------------|
| **vLLM** | Production inference | Medium |
| **Text-Generation-WebUI** | Personal use | Easy |
| **Ollama** | Easiest setup | Easy |
| **llama.cpp** | CPU inference | Medium |
| **TGI (HuggingFace)** | Enterprise | Hard |

---

## 6. Hardware Requirements

### The VRAM Formula

```
VRAM (GB) = Parameters (B) × 0.5  (for Q4 quantization)
VRAM (GB) = Parameters (B) × 1.0  (for Q8 quantization)
VRAM (GB) = Parameters (B) × 2.0  (for FP16)
```

### Complete Model Size Table

| Model | Q4 VRAM | Q8 VRAM | FP16 VRAM |
|-------|---------|---------|-----------|
| 7B | 4-5GB | 8GB | 14GB |
| 14B | 8-10GB | 16GB | 28GB |
| 32B | 18-20GB | 32GB | 64GB |
| 70B | 38-42GB | 70GB | 140GB |
| 72B | 40-45GB | 72GB | 144GB |
| 671B (DeepSeek) | 350GB+ | N/A | N/A |

### GPU Recommendations (2026)

#### NVIDIA Consumer GPUs

| GPU | VRAM | Best For | Price |
|-----|------|----------|-------|
| RTX 4060 | 8GB | 7-8B models | $300 |
| RTX 4070 | 12GB | 12-14B models | $550 |
| RTX 4070 Ti Super | 16GB | 14-20B models | $800 |
| **RTX 4090** | **24GB** | **32B models** | **$1600** |
| **RTX 5090** | **32GB** | **32B-40B models** | **$2000** |

#### NVIDIA Pro GPUs

| GPU | VRAM | Best For |
|-----|------|----------|
| RTX 6000 Ada | 48GB | 70B models |
| A100 80GB | 80GB | Large models |
| H100 80GB | 80GB | Enterprise |

#### Apple Silicon (Unified Memory)

| Device | RAM | Best For |
|--------|-----|----------|
| MacBook Pro M4 Max | 64GB | 32B models |
| MacBook Pro M4 Max | 128GB | 70B models |
| Mac Studio M4 Ultra | 192GB | 70B-120B models |

### Build Recommendations

#### Budget Build (~$500)
```
GPU: Used RTX 3060 12GB ($250)
CPU: Ryzen 5 5600 ($120)
RAM: 32GB DDR4 ($60)
Storage: 1TB NVMe ($60)
PSU: 650W ($50)

Runs: 7-14B models
```

#### Sweet Spot Build (~$2000)
```
GPU: RTX 4090 24GB ($1600)
CPU: Ryzen 7 7800X3D ($350)
RAM: 64GB DDR5 ($180)
Storage: 2TB NVMe ($120)

Runs: 32B models at good speed
```

#### Enthusiast Build (~$4000)
```
GPU: 2× RTX 4090 48GB total ($3200)
CPU: Ryzen 9 7950X ($400)
RAM: 128GB DDR5 ($350)

Runs: 70B models
```

---

## 7. Semantic Search & RAG Systems

### Complete RAG Solutions

#### All-in-One Tools

| Tool | Difficulty | Features | URL |
|------|------------|----------|-----|
| **AnythingLLM** | Easy | Full RAG, vector DB, chat UI | anythingllm.com |
| **Open WebUI** | Easy | ChatGPT-like UI, Ollama integration | github.com/open-webui |
| **GPT4All** | Easy | Desktop app, drag & drop | gpt4all.io |
| **LM Studio** | Easy | GUI + RAG | lmstudio.ai |
| **PrivateGPT** | Medium | 100% offline | github.com/zylon-ai/private-gpt |
| **LocalGPT** | Medium | Privacy-focused | github.com/PromtEngineer/localGPT |
| **Khoj** | Medium | Personal AI assistant | khoj.dev |
| **Danswer** | Medium | Enterprise search | danswer.ai |

#### How to Set Up Open WebUI + Ollama

```bash
# 1. Install Ollama
# Windows: Download from ollama.ai
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 2. Download models
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text

# 3. Start Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 4. Open http://localhost:3000
# 5. Upload documents
# 6. Chat!
```

### Build Your Own RAG Stack

#### Components

| Component | Options | Notes |
|-----------|---------|-------|
| **LLM Engine** | Ollama, llama.cpp, vLLM, TGI | vLLM fastest |
| **Embeddings** | nomic-embed-text, bge-large, e5-large | Run locally |
| **Vector DB** | ChromaDB, Qdrant, Milvus, pgvector | ChromaDB easiest |
| **Framework** | LangChain, LlamaIndex, Haystack | LlamaIndex for docs |
| **UI** | Open WebUI, Chainlit, Streamlit | Open WebUI most complete |

### Vector Database Comparison

| Database | Type | Best For | Difficulty |
|----------|------|----------|------------|
| **FAISS** | Library | Prototyping | Easy |
| **ChromaDB** | Embedded | Local apps | Easy |
| **Qdrant** | Server | Production | Medium |
| **Milvus** | Server | Enterprise | Hard |
| **pgvector** | Postgres | Existing DB | Easy |
| **Weaviate** | Server | Enterprise | Medium |
| **Pinecone** | Cloud | Managed | Easy |

---

## 8. Advanced RAG Techniques

### 8.1 Chunking Strategies

The way you split documents dramatically affects retrieval quality.

#### Chunking Methods Comparison

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| **Fixed Size** | Simple docs | Easy, predictable | Cuts mid-sentence |
| **Recursive** | Mixed content | Respects boundaries | May vary in size |
| **Semantic** | Meaningful content | Preserves meaning | Slower, needs model |
| **Document-Aware** | Structured docs | Respects structure | Format-specific |
| **Agentic** | Complex queries | Adaptive | Most complex |

#### Fixed Size Chunking

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_text(text)
```

#### Recursive Chunking (Recommended)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(text)
```

#### Semantic Chunking

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile"
)
chunks = splitter.split_text(text)
```

#### Multi-Scale Chunking (Advanced)

Index the same document at multiple chunk sizes for better retrieval:

```python
# Index at multiple sizes
chunk_sizes = [100, 200, 500, 1000]

for size in chunk_sizes:
    chunks = split_document(doc, chunk_size=size)
    store_in_vector_db(chunks, index_name=f"chunks_{size}")

# Retrieve from all and merge with RRF
def multi_scale_retrieve(query):
    results = []
    for size in chunk_sizes:
        results.append(search(query, index=f"chunks_{size}"))
    return reciprocal_rank_fusion(results)
```

### 8.2 Reranking

Reranking improves retrieval by re-ordering results with a more sophisticated model.

#### Why Rerank?

Initial retrieval is fast but approximate. Reranking uses a cross-encoder to score query-document pairs more accurately.

```python
# Without reranking: Top-k retrieval
results = vector_db.similarity_search(query, k=20)

# With reranking: Retrieve more, rerank, return fewer
results = vector_db.similarity_search(query, k=100)
reranked = reranker.rerank(query, results, top_k=10)
```

#### Reranking Models

| Model | Type | Speed | Accuracy |
|-------|------|-------|----------|
| **BGE-reranker-large** | Local | Medium | High |
| **Cohere rerank** | Cloud | Fast | High |
| **ColBERT** | Local | Slow | Very High |
| **Cross-encoder-ms-marco** | Local | Fast | Good |

#### Reranking Example

```python
from sentence_transformers import CrossEncoder

# Load reranker
reranker = CrossEncoder('BAAI/bge-reranker-large')

# Rerank results
pairs = [[query, doc.page_content] for doc in results]
scores = reranker.predict(pairs)

# Sort by score
reranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
```

### 8.3 Query Transformation

Transform user queries to improve retrieval.

#### Query Rewriting

```python
def rewrite_query(query, llm):
    prompt = f"""Rewrite this search query to be more specific and searchable:
    
Original: {query}
Rewritten:"""
    return llm.invoke(prompt)
```

#### Multi-Query

Generate multiple queries from one:

```python
def generate_multi_queries(query, llm):
    prompt = f"""Generate 3 different search queries that would help find information related to:
    
{query}

Queries:"""
    return llm.invoke(prompt).split('\n')
```

#### HyDE (Hypothetical Document Embeddings)

```python
def hyde_retrieve(query, llm, vector_db):
    # Generate hypothetical answer
    prompt = f"""Generate a hypothetical document that would answer this question:
    
{query}"""
    
    hypothetical = llm.invoke(prompt)
    
    # Search with hypothetical document
    results = vector_db.similarity_search(hypothetical, k=5)
    return results
```

### 8.4 Hybrid Search

Combine keyword (BM25) and semantic search:

```python
from rank_bm25 import BM25Okapi

def hybrid_search(query, vector_db, bm25_index, alpha=0.5):
    # Semantic search
    semantic_results = vector_db.similarity_search(query, k=20)
    semantic_scores = {r.id: r.score for r in semantic_results}
    
    # Keyword search
    keyword_results = bm25_index.get_top_n(query, k=20)
    keyword_scores = {r.id: r.score for r in keyword_results}
    
    # Combine scores
    all_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())
    combined = {}
    for id in all_ids:
        combined[id] = (
            alpha * semantic_scores.get(id, 0) +
            (1 - alpha) * keyword_scores.get(id, 0)
        )
    
    # Return top results
    return sorted(combined.items(), key=lambda x: x[1], reverse=True)[:10]
```

### 8.5 Contextual Compression

Compress retrieved context to fit more relevant information:

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor

# Create compressor
compressor = LLMChainExtractor.from_llm(llm)

# Create compression retriever
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vector_db.as_retriever()
)

# Retrieve compressed context
docs = compression_retriever.get_relevant_documents(query)
```

### 8.6 Parent Document Retriever

Retrieve small chunks but return larger context:

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Store parent documents
doc_store = InMemoryStore()

# Create retriever
retriever = ParentDocumentRetriever(
    vectorstore=vector_db,
    docstore=doc_store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)

# Index documents
retriever.add_documents(documents)

# Retrieve (returns parent documents)
results = retriever.get_relevant_documents(query)
```

### 8.7 RAG Evaluation

Evaluate your RAG system:

#### Metrics

| Metric | What It Measures |
|--------|------------------|
| **Faithfulness** | Is answer grounded in context? |
| **Answer Relevance** | Does answer address the question? |
| **Context Precision** | Is retrieved context relevant? |
| **Context Recall** | Did we retrieve all needed info? |

#### Tools

| Tool | Description |
|------|-------------|
| **Ragas** | RAG evaluation framework |
| **TruLens** | LLM app evaluation |
| **DeepEval** | Testing framework |

#### Ragas Example

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# Evaluate
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy]
)
print(results)
```

---

## 9. Document Processing Tools

### 9.1 PDF Processing

#### Docling (IBM) - Best Overall

**53K+ GitHub stars | 30x faster than OCR**

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")

# Export to markdown
markdown = result.document.export_to_markdown()

# Export to JSON (structured)
json_output = result.document.export_to_dict()
```

**Features:**
- Preserves tables, figures, layout
- Handles complex PDFs
- Fast (computer vision, not OCR)
- Multi-format support (PDF, DOCX, PPTX, images)

**Install:** `pip install docling`

---

#### GLM-OCR - Best for Complex Documents

**Multimodal OCR for complex document understanding**

```python
from glm_ocr import GLMOCR

ocr = GLMOCR()
result = ocr.process("complex_document.pdf")
```

**Features:**
- Handles charts, tables, formulas
- Multi-token prediction
- Complex layout understanding

---

#### Marker - Fast PDF to Markdown

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

models = create_model_dict()
converter = PdfConverter(models)
text = converter("document.pdf")
```

---

#### PyMuPDF4LLM - Fast Text Extraction

```python
import pymupdf4llm

text = pymupdf4llm.to_markdown("document.pdf")
```

---

#### PDF Benchmark Comparison

| Parser | Speed | Tables | Layout | Complex Docs |
|--------|-------|--------|--------|--------------|
| **Docling** | Fast | Excellent | Excellent | Excellent |
| **Marker** | Fast | Good | Good | Good |
| **PyMuPDF** | Very Fast | Basic | Basic | Fair |
| **pdfplumber** | Medium | Good | Fair | Fair |
| **PyPDF2** | Fast | Poor | Poor | Poor |
| **GPT-5.1 (LLM)** | Slow | Excellent | Excellent | Excellent |
| **Gemini 3 Pro** | Slow | Excellent | Excellent | Excellent |

---

### 9.2 Office Documents

| Tool | Formats | Notes |
|------|---------|-------|
| **python-docx** | .docx | Word documents |
| **openpyxl** | .xlsx | Excel files |
| **python-pptx** | .pptx | PowerPoint |
| **Unstructured** | All | Universal parser |

### 9.3 Code Processing

| Tool | Best For |
|------|----------|
| **tree-sitter** | AST-based parsing |
| **ast (Python)** | Python structure |
| **ripgrep** | Fast text search |
| **AST-grep** | Pattern matching |

### 9.4 Universal Parsers

#### Unstructured.io

```python
from unstructured.partition.auto import partition

# Auto-detects format
elements = partition(filename="any_file.xyz")
text = "\n\n".join([str(el) for el in elements])
```

---

## 10. Complete Comparison Tables

### All Models: Quick Reference

| Model | Params | Context | Local? | Reasoning? | Best For |
|-------|--------|---------|--------|------------|----------|
| Gemini 2.5 Pro | - | 1M | No | Yes | Largest context cloud |
| GPT-4.1 | - | 128K | No | Yes | General reasoning |
| GPT-4.1-preview | - | 128K | No | Yes | **Code understanding** |
| Claude Opus 4 | - | 200K | No | Yes | Deepest analysis |
| Claude Sonnet 4 | - | 200K | No | Yes | Balanced |
| DeepSeek V3 | 671B | 128K | Yes | No | Open flagship |
| DeepSeek R1 | 671B | 128K | Yes | **Yes** | Open reasoning |
| Llama 4 Scout | 17B | **10M** | Yes | No | **Massive context** |
| Llama 4 Maverick | 17B | 1M | Yes | No | Balanced local |
| Qwen3-Coder | 80B | 256K | Yes | No | Efficient coding |
| Qwen 2.5 Coder 32B | 32B | 32K | Yes | No | **Text analysis** |
| R1-Distill-32B | 32B | 128K | Yes | **Yes** | Reasoning local |

### Cloud Models: Pricing Comparison

| Model | Input $/1M | Output $/1M | Context |
|-------|------------|-------------|---------|
| Gemini 2.5 Pro | $1.25 | $5.00 | 1M |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M |
| GPT-4.1 | $2.50 | $10.00 | 128K |
| GPT-4.1-preview | $3.00 | $12.00 | 128K |
| Claude Opus 4 | $15.00 | $75.00 | 200K |
| Claude Sonnet 4 | $3.00 | $15.00 | 200K |
| DeepSeek V3 | $0.14 | $0.28 | 128K |
| DeepSeek R1 | $0.55 | $2.19 | 128K |
| Groq (Llama 4) | $0.59 | $0.79 | 8K |

### Local Models: VRAM Requirements

| Model | Q4 VRAM | GPU Needed |
|-------|---------|------------|
| Qwen 2.5 7B | 4-5GB | RTX 3060 8GB |
| Llama 4 Scout | 10GB | RTX 4070 Ti 16GB |
| Qwen 2.5 Coder 32B | 18-20GB | RTX 4090/5090 |
| R1-Distill-32B | 18-20GB | RTX 4090 24GB |
| Qwen 2.5 72B | 40-45GB | 2× RTX 4090 or Mac 128GB |
| Llama 4 Maverick | 10GB | RTX 4070 Ti 16GB |

### Archon RAG Implementation

Archon supports these models with enhanced RAG:

| Feature | Implementation | Setting |
|---------|----------------|---------|
| HyDE Query Transform | `search_with_hyde()` | `USE_HYDE=true` |
| Multi-Scale Chunking | `MultiScaleChunker` | `USE_MULTI_SCALE=true` |
| Parent Document Retrieval | `ParentDocumentRetriever` | `USE_PARENT_DOCS=true` |
| Contextual Compression | `ContextualCompressionRetriever` | `USE_COMPRESSION=true` |

---

## 11. Recommendations by Use Case

### Use Case 1: Codebase Understanding

**Best Cloud:** GPT-4.1-preview or Claude Code CLI

**Best Local:** Qwen 2.5 Coder 32B or Llama 4 Scout

**Best Fast:** Groq + Llama 4 Scout

---

### Use Case 2: Document/PDF Analysis

**Best Cloud:** Gemini 2.5 Pro (1M context)

**Best Local:** Qwen 2.5 Coder 32B + RAG

**Best Processing:** Docling + Llama 4 Scout

---

### Use Case 3: Chat History Analysis

**Best Cloud:** Gemini 2.5 Pro

**Best Local:** Llama 4 Scout (10M context)

---

### Use Case 4: Research Paper Analysis

**Best Cloud:** Claude Opus 4 or Gemini 2.5 Pro

**Best Local:** R1-Distill-32B (shows reasoning)

---

### Use Case 5: Privacy-Sensitive Documents

**Must Be Local:**
- AnythingLLM or PrivateGPT
- Qwen 2.5 Coder 32B or Llama 4 Scout

---

### Use Case 6: Budget-Conscious

**Free Cloud:** DeepSeek (deepseek.com) or Google AI Studio

**Budget Local:** RTX 3060 12GB + Qwen 2.5 7B/14B

---

### Use Case 7: Maximum Speed

**Fastest Inference:** Groq + Llama 4 Scout

**Speed:** 500+ tokens/second

---

### Use Case 8: Maximum Understanding

**The "Money No Object" Setup:**
- Cloud: Claude Opus 4 + Gemini 2.5 Pro
- Local: Mac Studio M4 Max 128GB + Llama 4 Scout
- RAG: Custom LlamaIndex + multi-scale chunking + reranking
- Processing: Docling for all documents

---

## 12. Quick Start Guides

### Quick Start: Gemini 2.5 Pro (Cloud - Largest Context)

1. Go to aistudio.google.com
2. Sign in with Google
3. Click "Create New Prompt"
4. Upload files (PDF, TXT, MD, images, video)
5. Ask questions

---

### Quick Start: Claude Code (CLI - Code Understanding)

```bash
npm install -g @anthropic-ai/claude-code
cd your-project
claude

# Ask questions
> What does this codebase do?
> Find all API endpoints
> Review for security issues
```

---

### Quick Start: Ollama + Open WebUI (Local - Easiest)

```bash
# Install Ollama from ollama.ai
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text

# Start Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

# Open localhost:3000
```

---

### Quick Start: LM Studio (Desktop - Simplest)

1. Download from lmstudio.ai
2. Search "qwen 2.5 coder 32b"
3. Click Download
4. Go to Chat tab
5. Drag documents into chat
6. Ask questions

---

### Quick Start: Groq (Fastest Inference)

```python
from groq import Groq

client = Groq(api_key="your-key")

response = client.chat.completions.create(
    model="llama-4-scout-17b-16e-instruct",
    messages=[{"role": "user", "content": "..."}]
)
```

---

### Quick Start: AnythingLLM (All-in-One)

```bash
docker run -d -p 3001:3001 anythingllm/anythingllm
# Open localhost:3001
# Create workspace
# Upload documents
# Chat
```

---

### Quick Start: DeepSeek R1 (Free Tier + Reasoning)

1. Go to chat.deepseek.com
2. Sign up (free)
3. Select "DeepThink" for reasoning
4. Upload files
5. See the reasoning chain

---

## 13. Code Examples

### Complete RAG Pipeline

```python
"""
Complete RAG Pipeline with all optimizations
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from sentence_transformers import CrossEncoder
import os

class DocumentRAG:
    def __init__(
        self,
        model_name="qwen2.5-coder:32b",
        embedding_model="nomic-embed-text",
        chunk_size=1000,
        chunk_overlap=200
    ):
        self.llm = Ollama(model=model_name)
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.reranker = CrossEncoder('BAAI/bge-reranker-large')
        self.vectorstore = None
        
    def load_documents(self, directory):
        """Load all documents from directory"""
        documents = []
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            if file.endswith('.pdf'):
                loader = PyPDFLoader(path)
            elif file.endswith('.txt') or file.endswith('.md'):
                loader = TextLoader(path)
            else:
                continue
            documents.extend(loader.load())
        return documents
    
    def index_documents(self, documents):
        """Split and index documents"""
        chunks = self.text_splitter.split_documents(documents)
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
    def retrieve_with_reranking(self, query, k=10):
        """Retrieve with reranking"""
        # Initial retrieval
        docs = self.vectorstore.similarity_search(query, k=20)
        
        # Rerank
        pairs = [[query, doc.page_content] for doc in docs]
        scores = self.reranker.predict(pairs)
        
        # Sort and return top k
        reranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in reranked[:k]]
    
    def query(self, question, use_reranking=True):
        """Query the RAG system"""
        if use_reranking:
            docs = self.retrieve_with_reranking(question)
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = f"""Based on the following context, answer the question.
            
Context:
{context}

Question: {question}

Answer:"""
            return self.llm.invoke(prompt)
        else:
            qa = RetrievalQA.from_chain_type(
                llm=self.llm,
                retriever=self.vectorstore.as_retriever()
            )
            return qa.invoke(question)

# Usage
rag = DocumentRAG()
documents = rag.load_documents("./my_documents")
rag.index_documents(documents)
response = rag.query("What is the main topic?")
```

### Multi-Modal Document Processing

```python
"""
Process multiple document types with Docling
"""

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption

class DocumentProcessor:
    def __init__(self):
        self.converter = DocumentConverter()
    
    def process(self, file_path):
        """Process any supported document"""
        result = self.converter.convert(file_path)
        
        return {
            'markdown': result.document.export_to_markdown(),
            'json': result.document.export_to_dict(),
            'text': result.document.export_to_text(),
            'tables': self._extract_tables(result),
            'figures': self._extract_figures(result)
        }
    
    def _extract_tables(self, result):
        """Extract tables from document"""
        tables = []
        for table in result.document.tables:
            tables.append(table.export_to_dataframe())
        return tables
    
    def _extract_figures(self, result):
        """Extract figures from document"""
        return [fig for fig in result.document.figures]

# Usage
processor = DocumentProcessor()
doc = processor.process("complex_report.pdf")
print(doc['markdown'])
```

### Fast Inference with Groq

```python
"""
Fast document Q&A with Groq
"""

from groq import Groq
import time

class FastDocumentQA:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.model = "llama-4-scout-17b-16e-instruct"
    
    def ask(self, context, question):
        """Fast query with context"""
        start = time.time()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}"
                }
            ],
            temperature=0.1,
            max_tokens=1024
        )
        
        elapsed = time.time() - start
        tokens = response.usage.total_tokens
        
        return {
            'answer': response.choices[0].message.content,
            'tokens': tokens,
            'time': elapsed,
            'tokens_per_second': tokens / elapsed
        }

# Usage
qa = FastDocumentQA(api_key="your-key")
result = qa.ask(document_text, "What are the key findings?")
print(f"Answer: {result['answer']}")
print(f"Speed: {result['tokens_per_second']:.0f} tokens/sec")
```

---

## 14. Resources & Links

### Official Documentation

| Resource | URL |
|----------|-----|
| Gemini API | ai.google.dev |
| OpenAI API | platform.openai.com |
| Anthropic API | docs.anthropic.com |
| Ollama | ollama.ai |
| LM Studio | lmstudio.ai |
| Hugging Face | huggingface.co |
| Groq | groq.com |

### Model Downloads

| Source | URL |
|--------|-----|
| Ollama Library | ollama.ai/library |
| Hugging Face | huggingface.co/models |
| Llama Official | llama.com |
| DeepSeek | github.com/deepseek-ai |

### Tools & Frameworks

| Tool | URL |
|------|-----|
| Open WebUI | github.com/open-webui/open-webui |
| AnythingLLM | anythingllm.com |
| PrivateGPT | github.com/zylon-ai/private-gpt |
| LangChain | python.langchain.com |
| LlamaIndex | docs.llamaindex.ai |
| Docling | github.com/docling-project/docling |

### Community

| Community | URL |
|-----------|-----|
| r/LocalLLaMA | reddit.com/r/LocalLLaMA |
| Hugging Face Discord | huggingface.co/join/discord |
| Ollama Discord | discord.gg/ollama |

### Benchmarks

| Benchmark | URL |
|-----------|-----|
| LMSYS Chatbot Arena | chat.lmsys.org |
| Open LLM Leaderboard | huggingface.co/spaces/open-llm-leaderboard |
| LiveCodeBench | livecodebench.github.io |

---

## Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Context Window** | Maximum tokens a model can process in one prompt |
| **Token** | ~0.75 words (roughly 4 characters) |
| **Embedding** | Vector representation of text capturing meaning |
| **RAG** | Retrieval Augmented Generation |
| **MoE** | Mixture of Experts - only uses subset of parameters |
| **Quantization** | Reducing precision to save memory (Q4, Q8) |
| **VRAM** | Video RAM - GPU memory for models |
| **Semantic Search** | Search by meaning, not keywords |
| **Chain of Thought** | Model shows its reasoning steps |
| **Distillation** | Training smaller model from larger one |
| **Reranking** | Re-ordering retrieved documents by relevance |
| **Hybrid Search** | Combining keyword and semantic search |
| **Chunking** | Splitting documents into smaller pieces |

---

### Appendix B: Model Family Trees

```
CLOUD MODELS (2026)
├── Google Gemini
│   ├── Gemini 2.5 Pro (flagship, 1M context, reasoning)
│   ├── Gemini 2.0 Flash (fast, 1M context)
│   └── Gemini 2.0 Flash-Lite (fastest, budget)
│
├── OpenAI GPT
│   ├── GPT-4.1 (reasoning, 128K context)
│   ├── GPT-4.1-mini (fast, budget)
│   └── GPT-4.1-preview (code specialist)
│
├── Anthropic Claude
│   ├── Claude Opus 4 (deepest, 200K context)
│   ├── Claude Sonnet 4 (balanced, 200K)
│   └── Claude Code (CLI tool)
│
├── DeepSeek
│   ├── DeepSeek V3 (open weights, 128K)
│   └── DeepSeek R1 (reasoning, API)
│
└── Others
    ├── Mistral Large 2
    ├── xAI Grok 2
    └── Cohere Command R+

OPEN MODELS (Can Run Locally)
├── Meta Llama 4
│   ├── Llama 4 Scout (10M context, 17B MoE, 10GB VRAM Q4)
│   ├── Llama 4 Maverick (1M context, 17B MoE)
│   └── Llama 4 Code (code specialist)
│
├── Qwen
│   ├── Qwen3-Coder (256K context, 80B MoE)
│   ├── Qwen 2.5 Coder 32B (text analysis)
│   └── Qwen 2.5 72B (general)
│
├── DeepSeek Distilled
│   ├── R1-Distill-Qwen-32B (reasoning, 18GB)
│   └── R1-Distill-Llama-70B (reasoning, 40GB)
│
└── Others
    ├── Microsoft Phi-4
    ├── Google Gemma 3
    └── 01.AI Yi-1.5

FAST INFERENCE APIs
├── Groq (LPU chips, 500+ tokens/sec)
├── Together AI (open models)
├── Fireworks AI (fast inference)
└── OpenRouter (unified API)
```

---

### Appendix F: Archon Integration Guide

Archon has built-in support for advanced RAG:

```python
# Enable enhanced features via environment:
USE_HYDE=true          # Hypothetical document embeddings
USE_RERANKING=true     # CrossEncoder reranking
USE_AGENTIC_RAG=true   # Code-aware search
USE_CONTEXTUAL=true    # Contextual embeddings
```

See `ARCHON_CODEBASE_REVIEW.md` for full implementation details.
