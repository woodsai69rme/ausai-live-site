# The Complete Guide to AI Models for Document Understanding & Reasoning

**Version 2.0 | February 2026**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [How AI Actually Understands Documents](#2-how-ai-actually-understands-documents)
3. [Cloud-Based Models](#3-cloud-based-models)
   - 3.1 [Google Gemini Family](#31-google-gemini-family)
   - 3.2 [OpenAI GPT Family](#32-openai-gpt-family)
   - 3.3 [Anthropic Claude Family](#33-anthropic-claude-family)
   - 3.4 [DeepSeek Family](#34-deepseek-family)
   - 3.5 [Other Cloud Providers](#35-other-cloud-providers)
4. [Open-Source & Local Models](#4-open-source--local-models)
   - 4.1 [Meta Llama 4 Family](#41-meta-llama-4-family)
   - 4.2 [Qwen Family](#42-qwen-family)
   - 4.3 [Other Open Models](#43-other-open-models)
5. [Hardware Requirements](#5-hardware-requirements)
6. [Semantic Search & RAG Systems](#6-semantic-search--rag-systems)
7. [Document Processing Tools](#7-document-processing-tools)
8. [Complete Comparison Tables](#8-complete-comparison-tables)
9. [Recommendations by Use Case](#9-recommendations-by-use-case)
10. [Quick Start Guides](#10-quick-start-guides)
11. [Resources & Links](#11-resources--links)

---

## 1. Introduction

### Why This Guide Exists

Most AI tools fail at actual document understanding. They perform keyword matching, not semantic reasoning. This guide covers the models, tools, and techniques that actually "read" and "understand" your documents.

### What You'll Learn

- The difference between keyword search vs semantic understanding
- Every major AI model available in 2026 (cloud and local)
- Hardware requirements for running models locally
- How to build systems that actually understand context
- Complete comparison tables for quick decisions

### Who This Is For

- Developers analyzing codebases
- Researchers working with papers and documentation
- Anyone who needs AI to actually understand their files
- People frustrated with "stupid" keyword-based tools

---

## 2. How AI Actually Understands Documents

### The Problem: Keyword vs Semantic

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

### Three Pillars of Document Understanding

#### Pillar 1: Context Window

The amount of text a model can process in a single prompt.

| Context Size | What It Fits |
|--------------|--------------|
| 4K tokens (~3K words) | ~2 pages |
| 32K tokens (~24K words) | ~15 pages |
| 128K tokens (~96K words) | ~60 pages, small codebase |
| 200K tokens (~150K words) | ~100 pages |
| 1M tokens (~750K words) | ~500 pages, entire book |
| 2M tokens (~1.5M words) | ~1000 pages, large codebase |
| 10M tokens (~7.5M words) | Massive codebases + history |

#### Pillar 2: Embeddings (Semantic Search)

Embeddings convert text into vectors (lists of numbers) that capture meaning.

```
"authentication" → [0.23, -0.45, 0.12, ...]
"login" → [0.21, -0.43, 0.15, ...]  (Similar!)
"banana" → [0.89, 0.12, -0.67, ...]  (Different!)
```

**Best Embedding Models:**
| Model | Dimensions | Best For |
|-------|------------|----------|
| nomic-embed-text | 768 | General purpose, fast |
| bge-large-en-v1.5 | 1024 | High accuracy |
| e5-large-v2 | 1024 | Multilingual |
| OpenAI text-embedding-3-large | 3072 | Cloud, high quality |
| Cohere embed-v4 | 1024 | Enterprise |

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
│  Documents  │ ──► │  Embeddings  │ ──► │  Vector DB  │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                    ┌──────────────┐            │
                    │   Your Query │            │
                    └──────────────┘            │
                           │                    │
                           ▼                    ▼
                    ┌──────────────────────────────┐
                    │     Semantic Search          │
                    │  (Find relevant chunks)      │
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

#### Gemini 3.1 Pro (Latest - Feb 2026)

**The Flagship**

| Specification | Value |
|---------------|-------|
| Context Window | **1M tokens** (~750K words) |
| Multimodal | Text, images, audio, video |
| Reasoning | Advanced agentic reasoning |
| Training Data | Up to early 2026 |
| Access | Google AI Studio, Vertex AI |

**Best For:**
- Processing entire codebases at once
- Analyzing multiple large documents
- Multimodal tasks (docs + images + video)
- Agentic workflows

**Pricing:**
| Tier | Input | Output |
|------|-------|--------|
| Standard | $1.25/1M tokens | $5.00/1M tokens |
| With context caching | $0.31/1M tokens | $5.00/1M tokens |

**How to Use:**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click "Create New Prompt"
3. Upload files (PDF, TXT, MD, images, video)
4. Ask questions with full context

**Example Prompts:**
```
"Analyze all these documents and identify the main themes"
"Review this codebase and explain the architecture"
"Compare these three papers and identify contradictions"
"What are the security vulnerabilities in this code?"
```

---

#### Gemini 2.5 Pro

**The Previous Flagship (Still Excellent)**

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Video Processing | Up to 3 hours |
| Thinking Model | Yes, with extended reasoning |

**Best For:**
- Video analysis
- Complex reasoning tasks
- Cost-sensitive large context needs

---

#### Gemini 2.0 Flash

**The Speed Champion**

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Speed | Very fast |
| Cost | Low |

**Best For:**
- High-volume processing
- Quick document summaries
- Batch processing many files

---

### 3.2 OpenAI GPT Family

#### GPT-5.2 (Current Flagship)

**The Unified System**

| Specification | Value |
|---------------|-------|
| Context Window | 128K tokens |
| Thinking Mode | Built-in, automatic |
| Knowledge Cutoff | Early 2026 |

**Key Features:**
- Automatically knows when to "think" longer
- Expert-level coding and math
- Unified system (no model selection needed)
- Lower hallucination rate

**Best For:**
- General reasoning tasks
- Writing and editing
- Complex problem-solving

**Pricing:**
| Tier | Input | Output |
|------|-------|--------|
| Standard | $2.50/1M tokens | $10.00/1M tokens |

---

#### GPT-5.3-Codex (Feb 2026)

**The Code Specialist**

| Specification | Value |
|---------------|-------|
| Context Window | 128K tokens |
| Speed | 25% faster than GPT-5.2 |
| Focus | Agentic coding |

**Best For:**
- **Code review and understanding**
- Debugging complex systems
- Code generation with reasoning
- Analyzing codebases

**This is THE model for code understanding.**

---

#### GPT-5.2 Instant

**The Speed Option**

| Specification | Value |
|---------------|-------|
| Context Window | 128K tokens |
| Speed | Fastest GPT-5 variant |

**Best For:**
- Quick queries
- High-volume chat
- Simple tasks

---

#### GPT-OSS (Open Source Variant)

**Self-Hostable GPT**

OpenAI released an open-source variant that can be run on your own infrastructure.

**Best For:**
- Privacy-sensitive applications
- Air-gapped environments
- Custom fine-tuning

---

### 3.3 Anthropic Claude Family

#### Claude Opus 4

**The Deepest Thinker**

| Specification | Value |
|---------------|-------|
| Context Window | 200K tokens (~150K words) |
| Thinking | Extended thinking mode |
| Specialty | Complex analysis |

**Best For:**
- Nuanced reasoning
- Research synthesis
- Legal/medical document analysis
- Tasks requiring careful consideration

**Pricing:**
| Tier | Input | Output |
|------|-------|--------|
| Standard | $15.00/1M tokens | $75.00/1M tokens |
| With extended thinking | Higher | Higher |

---

#### Claude Sonnet 4

**The Balanced Choice**

| Specification | Value |
|---------------|-------|
| Context Window | 200K tokens |
| Speed | 3x faster than Opus |
| Cost | 1/5 of Opus |

**Best For:**
- Daily workhorse tasks
- Code understanding
- Document analysis
- Most common use cases

**Pricing:**
| Tier | Input | Output |
|------|-------|--------|
| Standard | $3.00/1M tokens | $15.00/1M tokens |

---

#### Claude Code (CLI Tool)

**The Developer's Friend**

Claude Code is Anthropic's command-line tool for code understanding.

**Features:**
- Direct file system access
- Reads your actual files
- Makes edits with your approval
- Runs commands
- Full codebase awareness

**How to Use:**
```bash
# Install
npm install -g @anthropic-ai/claude-code

# Run on a directory
claude --dir ./my-project

# Ask questions
> "What does the authentication system do?"
> "Find all uses of the deprecated API"
> "Review this code for security issues"
```

**Best For:**
- Code review
- Codebase exploration
- Automated refactoring
- Documentation generation

---

### 3.4 DeepSeek Family

**The Open-Weight Revolution**

DeepSeek changed everything by releasing GPT-5 class models with open weights.

#### DeepSeek V3.2 (Current Flagship)

| Specification | Value |
|---------------|-------|
| Parameters | 671B (MoE - only 37B active) |
| Context Window | 128K tokens |
| Performance | Matches GPT-5, Gemini 3 |
| License | MIT (fully open) |

**Best For:**
- Running GPT-5 level locally (with enough hardware)
- Custom fine-tuning
- Privacy-sensitive applications

**Hardware to Run:**
- Requires 350GB+ VRAM (multi-GPU server)
- Use distilled versions for consumer hardware

---

#### DeepSeek R1

**The Reasoning Specialist**

| Specification | Value |
|---------------|-------|
| Base | DeepSeek V3 |
| Specialty | Chain-of-thought reasoning |
| Transparency | Shows thinking process |

**Key Innovation:**
DeepSeek R1 was trained with pure reinforcement learning to develop reasoning. It shows its work:

```
User: "Is 17077 a prime number?"

R1 Thinking:
Let me work through this systematically.
First, I'll check divisibility by small primes...
17077 ÷ 2 = no (odd number)
17077 ÷ 3 = 5,692.33... no
...
17077 = 73 × 233

Therefore, 17077 is NOT prime.
```

**Best For:**
- Math problems
- Logic puzzles
- Complex reasoning tasks
- When you need to see the "thinking"

---

#### DeepSeek R1 Distilled Models

**Reasoning for Consumer Hardware**

| Model | Parameters | VRAM Needed (Q4) |
|-------|------------|------------------|
| R1-Distill-Qwen-1.5B | 1.5B | 1GB |
| R1-Distill-Qwen-7B | 7B | 4GB |
| R1-Distill-Qwen-14B | 14B | 8GB |
| R1-Distill-Qwen-32B | 32B | 18GB |
| R1-Distill-Llama-70B | 70B | 40GB |

**Best Value:** R1-Distill-Qwen-32B runs on RTX 4090 and has excellent reasoning.

---

### 3.5 Other Cloud Providers

#### Mistral AI

| Model | Context | Best For |
|-------|---------|----------|
| Mistral Large 2 | 128K | General reasoning |
| Codestral | 32K | Code generation |
| Mixtral 8x22B | 65K | Open-weight, efficient |

#### xAI Grok

| Model | Context | Best For |
|-------|---------|----------|
| Grok 2 | 131K | Real-time info (X integration) |

#### Cohere

| Model | Context | Best For |
|-------|---------|----------|
| Command R+ | 128K | Enterprise RAG |
| Command R | 128K | Efficient RAG |

#### Amazon Bedrock

Provides access to multiple models:
- Claude (Anthropic)
- Llama (Meta)
- Titan (Amazon)
- Mistral

---

## 4. Open-Source & Local Models

### 4.1 Meta Llama 4 Family

**The Open-Source Leader**

Meta's Llama 4 family is fully open-source with industry-leading capabilities.

#### Llama 4 Scout

**The Context King**

| Specification | Value |
|---------------|-------|
| Context Window | **10M tokens** (~7.5M words) |
| Parameters | 17B (MoE, ~3B active) |
| License | Llama Community License |
| Multimodal | Yes |

**This is INSANE for local use.** 10M tokens means:
- Entire large codebases in one context
- Years of chat history
- Complete documentation libraries

**Hardware Requirements:**
| Quantization | VRAM | Example GPU |
|--------------|------|-------------|
| Q4_K_M | 10GB | RTX 4070 Ti Super |
| Q8 | 18GB | RTX 4090 |
| FP16 | 34GB | Mac M4 Max 64GB |

---

#### Llama 4 Maverick

**The Balanced Choice**

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Parameters | 17B (MoE, ~3B active) |
| Multimodal | Yes |

**Best For:**
- Balanced performance/cost
- Multimodal tasks
- General purpose use

---

#### Llama 4 Behemoth

**The Teacher Model**

| Specification | Value |
|---------------|-------|
| Context Window | 1M tokens |
| Active Parameters | 288B |
| Role | Teacher model for distillation |

**Note:** Available but requires serious infrastructure (multi-GPU).

---

#### Llama 4 Code

**The Code Specialist**

Specialized for code understanding and generation.

**Best For:**
- Code review
- Code completion
- Bug detection
- Code explanation

---

### 4.2 Qwen Family

**Alibaba's Open Models**

#### Qwen3-Coder-Next (Feb 2026)

**The Efficient Coder**

| Specification | Value |
|---------------|-------|
| Parameters | 80B total, 3B active (MoE) |
| Context Window | **256K tokens** |
| License | Apache 2.0 |

**Why It's Special:**
- Only 3B parameters active per token
- Frontier-level coding performance
- Runs on consumer hardware
- Massive 256K context

**Hardware:**
| Quantization | VRAM | Example GPU |
|--------------|------|-------------|
| Q4_K_M | 5GB | RTX 4060 |
| Q8 | 8GB | RTX 4070 |

---

#### Qwen 2.5 Coder 32B

**The Text Analysis Champion**

| Specification | Value |
|---------------|-------|
| Parameters | 32B |
| Context Window | 32K tokens |
| Specialty | Code AND text analysis |

**Why It's Special:**
Reddit user discovered: "Qwen 2.5 32b Coder is the best local text analysis LLM I can find. It really mirrors the source text and can explore very nuanced details."

**Hardware:**
| Quantization | VRAM | Example GPU |
|--------------|------|-------------|
| Q4_K_M | 18GB | RTX 4090/5090 |
| Q8 | 32GB | Mac M4 Max |

**This is THE recommended local model for document understanding.**

---

#### Qwen 2.5 72B

**The Large Option**

| Specification | Value |
|---------------|-------|
| Parameters | 72B |
| Context Window | 128K tokens |

**Hardware:**
| Quantization | VRAM | Example |
|--------------|------|---------|
| Q4_K_M | 40GB | 2× RTX 4090 or Mac M4 Max 128GB |

---

### 4.3 Other Open Models

#### Mixtral Family (Mistral AI)

| Model | Params | Context | Best For |
|-------|--------|---------|----------|
| Mixtral 8x7B | 47B (12B active) | 32K | Efficient general |
| Mixtral 8x22B | 141B (39B active) | 65K | Large open model |

#### Yi Family (01.AI)

| Model | Params | Context | Best For |
|-------|--------|---------|----------|
| Yi-1.5-34B | 34B | 32K | General purpose |

#### Phi Family (Microsoft)

| Model | Params | Context | Best For |
|-------|--------|---------|----------|
| Phi-4 | 14B | 16K | Small, efficient, reasoning |

#### Gemma Family (Google)

| Model | Params | Context | Best For |
|-------|--------|---------|----------|
| Gemma 2 27B | 27B | 8K | General purpose |
| Gemma 3 | Varies | Varies | Latest generation |

---

## 5. Hardware Requirements

### The VRAM Formula

**Quick Calculation:**
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
| 120B | 65-70GB | 120GB | 240GB |
| 671B (DeepSeek) | 350GB+ | N/A | N/A |

### GPU Recommendations (2026)

#### NVIDIA Consumer GPUs

| GPU | VRAM | Best For | Price Range |
|-----|------|----------|-------------|
| RTX 4060 | 8GB | 7-8B models | $300 |
| RTX 4070 | 12GB | 12-14B models | $550 |
| RTX 4070 Ti Super | 16GB | 14-20B models | $800 |
| RTX 4080 Super | 16GB | 14-20B models | $1000 |
| **RTX 4090** | **24GB** | **32B models** | **$1600** |
| **RTX 5090** | **32GB** | **32B-40B models** | **$2000** |

#### NVIDIA Pro GPUs

| GPU | VRAM | Best For |
|-----|------|----------|
| RTX 6000 Ada | 48GB | 70B models (single card) |
| A6000 | 48GB | 70B models |
| A100 80GB | 80GB | Large models, multi-instance |
| H100 80GB | 80GB | Enterprise training/inference |

#### AMD GPUs

| GPU | VRAM | Notes |
|-----|------|-------|
| RX 7900 XTX | 24GB | ROCm support improving |
| RX 7900 XT | 20GB | Good value |
| Instinct MI300X | 192GB | Enterprise |

#### Apple Silicon (Unified Memory)

| Device | RAM | Best For |
|--------|-----|----------|
| MacBook Pro M4 Pro | 36GB | 14B models |
| MacBook Pro M4 Max | 64GB | 32B models |
| MacBook Pro M4 Max | 128GB | 70B models |
| Mac Studio M4 Max | 128GB | 70B models |
| Mac Studio M4 Ultra | 192GB | 70B-120B models |

**Why Mac for Local AI:**
- Unified memory = all RAM available for models
- No VRAM limitation like discrete GPUs
- Excellent power efficiency
- Great for 32B-70B models

### Build Recommendations

#### Budget Build (~$500)
```
GPU: Used RTX 3060 12GB ($250)
CPU: Ryzen 5 5600 ($120)
RAM: 32GB DDR4 ($60)
Storage: 1TB NVMe ($60)
PSU: 650W ($50)

Runs: 7-14B models comfortably
```

#### Sweet Spot Build (~$2000)
```
GPU: RTX 4090 24GB ($1600)
CPU: Ryzen 7 7800X3D ($350)
RAM: 64GB DDR5 ($180)
Storage: 2TB NVMe ($120)
PSU: 850W ($100)
Case: Good airflow ($100)

Runs: 32B models at good speed
```

#### Enthusiast Build (~$4000)
```
GPU: 2× RTX 4090 48GB total ($3200)
CPU: Ryzen 9 7950X ($400)
RAM: 128GB DDR5 ($350)
Storage: 4TB NVMe ($200)
PSU: 1200W ($200)

Runs: 70B models at good speed
```

#### Mac Studio Build (~$6000)
```
Mac Studio M4 Max
128GB Unified Memory
2TB Storage

Runs: 70B models efficiently
Zero configuration needed
```

### Storage Requirements

Models are large. Plan storage accordingly:

| Model Size | File Size (Q4) | File Size (FP16) |
|------------|----------------|------------------|
| 7B | 4-5GB | 14GB |
| 14B | 8-10GB | 28GB |
| 32B | 18-20GB | 64GB |
| 70B | 40-45GB | 140GB |
| 671B | 350GB+ | 1.3TB+ |

**Recommendation:** 2TB+ NVMe SSD for model storage.

---

## 6. Semantic Search & RAG Systems

### Complete RAG Solutions

#### All-in-One Tools

| Tool | Difficulty | Features |
|------|------------|----------|
| **AnythingLLM** | Easy | Full RAG system, vector DB included, chat UI |
| **Open WebUI** | Easy | ChatGPT-like UI, Ollama integration, RAG |
| **GPT4All** | Easy | Desktop app, drag & drop docs |
| **LM Studio** | Easy | GUI for models + RAG, easy setup |
| **PrivateGPT** | Medium | 100% offline, production-ready |
| **LocalGPT** | Medium | Privacy-focused RAG |

#### How to Set Up Open WebUI + Ollama

```bash
# 1. Install Ollama
# Windows: Download from ollama.ai
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 2. Download a model
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text  # For embeddings

# 3. Install Open WebUI (Docker)
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 4. Open http://localhost:3000
# 5. Upload documents in the "Documents" section
# 6. Enable RAG in settings
# 7. Chat with your documents!
```

#### How to Set Up LM Studio

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Open the app
3. Search for and download a model (e.g., "qwen 2.5 coder 32b")
4. Go to "Chat" tab
5. Drag your documents into the chat
6. Enable "Use RAG" if prompted
7. Start chatting with your documents

### Build Your Own RAG Stack

#### Components

| Component | Options | Notes |
|-----------|---------|-------|
| **LLM Engine** | Ollama, llama.cpp, vLLM, Text-Generation-WebUI | vLLM fastest, Ollama easiest |
| **Embeddings** | nomic-embed-text, bge-large, e5-large | Run locally with Ollama |
| **Vector DB** | ChromaDB, Qdrant, Milvus, pgvector, FAISS | ChromaDB easiest, Qdrant scalable |
| **Framework** | LangChain, LlamaIndex, Haystack | LlamaIndex for docs, LangChain general |
| **UI** | Open WebUI, Chainlit, Streamlit, Gradio | Open WebUI most complete |

#### Example: LangChain + ChromaDB

```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Load documents
loader = PyPDFLoader("your_document.pdf")
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)

# Create embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Store in vector database
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# Create RAG chain
llm = Ollama(model="qwen2.5-coder:32b")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query
response = qa.invoke("What is this document about?")
print(response)
```

#### Example: LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

# Load all documents from a directory
documents = SimpleDirectoryReader("./your_docs").load_data()

# Configure models
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
Settings.llm = Ollama(model="qwen2.5-coder:32b")

# Create index
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("Summarize the main points")
print(response)
```

### Vector Database Comparison

| Database | Type | Best For | Difficulty |
|----------|------|----------|------------|
| **FAISS** | Library | Prototyping, local | Easy |
| **ChromaDB** | Embedded | Local apps, easy setup | Easy |
| **Qdrant** | Server | Production, scalable | Medium |
| **Milvus** | Server | Enterprise, huge scale | Hard |
| **pgvector** | Postgres extension | Existing Postgres users | Easy |
| **Weaviate** | Server | Enterprise features | Medium |
| **Pinecone** | Cloud | Managed, no ops | Easy |

---

## 7. Document Processing Tools

### Before the LLM: Document Parsing

Raw files need processing before LLMs can understand them.

#### For PDFs

| Tool | Best For | Features |
|------|----------|----------|
| **Docling** | Complex PDFs | Tables, figures, layout preservation |
| **Marker** | Fast conversion | PDF → Markdown, good tables |
| **PyMuPDF4LLM** | Text extraction | Fast, handles images |
| **PyPDF2** | Simple PDFs | Basic text extraction |
| **pdfplumber** | Tables | Good table extraction |

#### Docling Example (Recommended)

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("your_document.pdf")

# Get markdown output
markdown = result.document.export_to_markdown()

# Get structured output
json_output = result.document.export_to_dict()
```

#### For Code

| Tool | Best For |
|------|----------|
| **tree-sitter** | AST-based parsing |
| **ast (Python)** | Python code structure |
| **ripgrep** | Fast text search |

#### For Office Documents

| Tool | Formats |
|------|---------|
| **python-docx** | .docx |
| **openpyxl** | .xlsx |
| **python-pptx** | .pptx |

#### Unstructured.io (Universal)

```python
from unstructured.partition.auto import partition

# Automatically detects format
elements = partition(filename="any_file.pdf")
text = "\n\n".join([str(el) for el in elements])
```

### Chunking Strategies

How you split documents matters.

| Strategy | Best For | Code |
|----------|----------|------|
| **Fixed size** | Simple docs | `chunk_size=1000` |
| **Recursive** | Mixed content | LangChain RecursiveCharacterTextSplitter |
| **Semantic** | Preserving meaning | Embeddings-based |
| **Code-aware** | Source code | Split by functions/classes |

```python
# Recursive (recommended)
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# Code-aware
from langchain.text_splitter import PythonCodeTextSplitter

splitter = PythonCodeTextSplitter(chunk_size=1000)
```

---

## 8. Complete Comparison Tables

### All Models: Quick Reference

| Model | Params | Context | Local? | Reasoning? | Best For |
|-------|--------|---------|--------|------------|----------|
| **Gemini 3.1 Pro** | - | 1M | No | Yes | Largest context cloud |
| **GPT-5.2** | - | 128K | No | Yes | General reasoning |
| **GPT-5.3-Codex** | - | 128K | No | Yes | **Code understanding** |
| **Claude Opus 4** | - | 200K | No | Yes | Deepest analysis |
| **Claude Sonnet 4** | - | 200K | No | Yes | Balanced |
| **DeepSeek V3.2** | 671B MoE | 128K | Yes | No | Open flagship |
| **DeepSeek R1** | 671B MoE | 128K | Yes | **Yes** | Open reasoning |
| **Llama 4 Scout** | 17B MoE | **10M** | Yes | No | **Massive context local** |
| **Llama 4 Maverick** | 17B MoE | 1M | Yes | No | Balanced local |
| **Qwen3-Coder-Next** | 80B MoE | 256K | Yes | No | Efficient coding |
| **Qwen 2.5 Coder 32B** | 32B | 32K | Yes | No | **Text analysis local** |
| **R1-Distill-32B** | 32B | 128K | Yes | **Yes** | Reasoning on 24GB GPU |

### Cloud Models: Pricing Comparison

| Model | Input $/1M | Output $/1M | Context |
|-------|------------|-------------|---------|
| Gemini 3.1 Pro | $1.25 | $5.00 | 1M |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1M |
| GPT-5.2 | $2.50 | $10.00 | 128K |
| GPT-5.3-Codex | $3.00 | $12.00 | 128K |
| Claude Opus 4 | $15.00 | $75.00 | 200K |
| Claude Sonnet 4 | $3.00 | $15.00 | 200K |
| DeepSeek V3.2 API | $0.14 | $0.28 | 128K |
| DeepSeek R1 API | $0.55 | $2.19 | 128K |

### Local Models: VRAM Requirements

| Model | Q4 VRAM | GPU Needed |
|-------|---------|------------|
| Qwen 2.5 7B | 4-5GB | RTX 3060 8GB |
| Llama 4 Scout | 10GB | RTX 4070 Ti 16GB |
| Qwen 2.5 Coder 32B | 18-20GB | RTX 4090 24GB |
| R1-Distill-32B | 18-20GB | RTX 4090 24GB |
| Qwen 2.5 72B | 40-45GB | 2× RTX 4090 or Mac 128GB |
| Llama 4 Maverick | 10GB | RTX 4070 Ti 16GB |

---

## 9. Recommendations by Use Case

### Use Case 1: Codebase Understanding

**Best Cloud:**
```
GPT-5.3-Codex via ChatGPT or API
OR
Claude Code CLI
```

**Best Local:**
```
Qwen 2.5 Coder 32B on RTX 4090/5090
OR
Llama 4 Scout for massive codebases (10M context)
```

**Setup:**
```bash
# Option A: Claude Code
claude --dir ./your-codebase

# Option B: Open WebUI + Ollama
ollama pull qwen2.5-coder:32b
# Upload codebase as documents, chat
```

---

### Use Case 2: Document/PDF Analysis

**Best Cloud:**
```
Gemini 3.1 Pro - Upload all documents at once (1M context)
```

**Best Local:**
```
Qwen 2.5 Coder 32B + RAG system
OR
Llama 4 Scout if docs fit in 10M tokens
```

**Setup:**
```bash
# Using AnythingLLM (easiest)
docker run -d -p 3001:3001 anythingllm/anythingllm
# Open localhost:3001, upload docs, chat

# Using Open WebUI
# Upload documents in Documents section, enable in chat
```

---

### Use Case 3: Chat History Analysis

**Best Cloud:**
```
Gemini 3.1 Pro - Paste/attach all history (1M context)
OR
Claude Sonnet 4 for nuanced analysis
```

**Best Local:**
```
Llama 4 Scout - 10M context handles years of history
```

**Setup:**
```bash
# Export chat history to text files
# Upload to Gemini AI Studio or use with local model
```

---

### Use Case 4: Research Paper Analysis

**Best Cloud:**
```
Claude Opus 4 - Deepest reasoning
OR
Gemini 3.1 Pro - Multiple papers at once
```

**Best Local:**
```
R1-Distill-32B - Shows reasoning chain
```

---

### Use Case 5: Privacy-Sensitive Documents

**Must Be Local:**
```
AnythingLLM or PrivateGPT
+ Qwen 2.5 Coder 32B or Llama 4 Scout
```

**No internet required. All data stays on your machine.**

---

### Use Case 6: Budget-Conscious

**Free Cloud:**
```
DeepSeek V3.2 or R1 via deepseek.com
OR
Google AI Studio (Gemini Flash free tier)
```

**Budget Local:**
```
Used RTX 3060 12GB ($250)
+ Qwen 2.5 7B or 14B
```

---

### Use Case 7: Maximum Understanding

**The "Money No Object" Setup:**
```
Cloud: Claude Opus 4 + Gemini 3.1 Pro
Local: Mac Studio M4 Max 128GB + Llama 4 Scout
RAG: Custom LlamaIndex pipeline with multiple embeddings
```

---

## 10. Quick Start Guides

### Quick Start: Gemini 3.1 Pro (Cloud)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with Google account
3. Click "Create New Prompt"
4. Upload your files (PDF, TXT, MD, images, video)
5. Type your question
6. Get answers with full context understanding

**Cost:** Free tier available, then pay per token

---

### Quick Start: Claude Code (CLI)

```bash
# Install
npm install -g @anthropic-ai/claude-code

# Navigate to your project
cd your-project

# Start Claude Code
claude

# Ask questions
> What does this codebase do?
> Find all API endpoints
> Review authentication for security issues

# Claude reads your files and responds with context
```

**Cost:** Uses Anthropic API (pay per token)

---

### Quick Start: Ollama + Open WebUI (Local)

```bash
# 1. Install Ollama
# Download from ollama.ai

# 2. Pull a model
ollama pull qwen2.5-coder:32b
ollama pull nomic-embed-text

# 3. Start Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main

# 4. Open http://localhost:3000
# 5. Select your model
# 6. Upload documents
# 7. Chat!
```

**Cost:** Free after hardware

---

### Quick Start: LM Studio (Local - Easiest)

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Open the app
3. Search for "qwen 2.5 coder 32b"
4. Click Download
5. Go to Chat tab
6. Select the model
7. Drag documents into chat
8. Ask questions

**Cost:** Free after hardware

---

### Quick Start: AnythingLLM (All-in-One)

```bash
# Docker
docker run -d -p 3001:3001 anythingllm/anythingllm

# Or download desktop app from anythingllm.com
```

1. Open http://localhost:3001
2. Create workspace
3. Upload documents
4. Chat with full RAG

**Cost:** Free for personal use

---

### Quick Start: DeepSeek R1 (Cloud - Free Tier)

1. Go to [chat.deepseek.com](https://chat.deepseek.com)
2. Sign up (free)
3. Select "DeepThink" for reasoning
4. Upload files or paste content
5. Ask questions
6. See the reasoning chain

**Cost:** Free tier available

---

## 11. Resources & Links

### Official Documentation

| Resource | URL |
|----------|-----|
| Gemini API | [ai.google.dev](https://ai.google.dev) |
| OpenAI API | [platform.openai.com](https://platform.openai.com) |
| Anthropic API | [docs.anthropic.com](https://docs.anthropic.com) |
| Ollama | [ollama.ai](https://ollama.ai) |
| LM Studio | [lmstudio.ai](https://lmstudio.ai) |
| Hugging Face | [huggingface.co](https://huggingface.co) |

### Model Downloads

| Source | URL |
|--------|-----|
| Ollama Library | [ollama.ai/library](https://ollama.ai/library) |
| Hugging Face | [huggingface.co/models](https://huggingface.co/models) |
| Llama Official | [llama.com](https://llama.com) |
| DeepSeek | [github.com/deepseek-ai](https://github.com/deepseek-ai) |

### Tools & Frameworks

| Tool | URL |
|------|-----|
| Open WebUI | [github.com/open-webui/open-webui](https://github.com/open-webui/open-webui) |
| AnythingLLM | [anythingllm.com](https://anythingllm.com) |
| PrivateGPT | [github.com/zylon-ai/private-gpt](https://github.com/zylon-ai/private-gpt) |
| LangChain | [python.langchain.com](https://python.langchain.com) |
| LlamaIndex | [docs.llamaindex.ai](https://docs.llamaindex.ai) |
| Docling | [github.com/docling-project/docling](https://github.com/docling-project/docling) |

### Community

| Community | URL |
|-----------|-----|
| r/LocalLLaMA | [reddit.com/r/LocalLLaMA](https://reddit.com/r/LocalLLaMA) |
| Hugging Face Discord | [huggingface.co/join/discord](https://huggingface.co/join/discord) |
| Ollama Discord | [discord.gg/ollama](https://discord.gg/ollama) |

### Benchmarks

| Benchmark | URL |
|-----------|-----|
| LMSYS Chatbot Arena | [chat.lmsys.org](https://chat.lmsys.org) |
| Open LLM Leaderboard | [huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard) |
| LiveCodeBench | [livecodebench.github.io](https://livecodebench.github.io) |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Context Window** | Maximum tokens a model can process in one prompt |
| **Token** | ~0.75 words (roughly 4 characters) |
| **Embedding** | Vector representation of text capturing meaning |
| **RAG** | Retrieval Augmented Generation - combine search with LLM |
| **MoE** | Mixture of Experts - only uses subset of parameters |
| **Quantization** | Reducing precision to save memory (Q4, Q8) |
| **VRAM** | Video RAM - GPU memory for models |
| **Semantic Search** | Search by meaning, not keywords |
| **Chain of Thought** | Model shows its reasoning steps |
| **Distillation** | Training smaller model from larger one |

---

## Appendix B: Model Family Trees

```
CLOUD MODELS
├── Google Gemini
│   ├── Gemini 3.1 Pro (flagship, 1M context)
│   ├── Gemini 2.5 Pro (previous flagship)
│   ├── Gemini 2.0 Flash (fast)
│   └── Gemini 2.0 Flash-Lite (fastest)
│
├── OpenAI GPT
│   ├── GPT-5.2 (unified system)
│   ├── GPT-5.2 Instant (fast)
│   ├── GPT-5.3-Codex (code specialist)
│   └── GPT-OSS (open source)
│
├── Anthropic Claude
│   ├── Claude Opus 4 (deepest)
│   ├── Claude Sonnet 4 (balanced)
│   └── Claude Code (CLI tool)
│
├── DeepSeek (Open Weights)
│   ├── DeepSeek V3.2 (general)
│   └── DeepSeek R1 (reasoning)
│       └── R1 Distills (32B, 70B, etc.)
│
└── Others
    ├── Mistral Large 2
    ├── xAI Grok 2
    └── Cohere Command R+

OPEN MODELS (Can Run Locally)
├── Meta Llama 4
│   ├── Llama 4 Scout (10M context!)
│   ├── Llama 4 Maverick (balanced)
│   ├── Llama 4 Behemoth (largest)
│   └── Llama 4 Code (code specialist)
│
├── Qwen
│   ├── Qwen3-Coder-Next (80B MoE, 256K context)
│   ├── Qwen 2.5 Coder 32B (best text analysis)
│   └── Qwen 2.5 72B (large)
│
├── Mistral
│   ├── Mixtral 8x7B
│   └── Mixtral 8x22B
│
└── Others
    ├── Microsoft Phi-4
    ├── Google Gemma 2/3
    └── 01.AI Yi
```

---

## Appendix C: Decision Flowchart

```
START: Need document understanding?
│
├── Privacy required? ──────────────────► LOCAL MODELS
│   │
│   ├── Budget hardware? (8-16GB VRAM)
│   │   └── Qwen 2.5 Coder 32B or Llama 4 Scout
│   │
│   └── Good hardware? (24GB+ VRAM)
│       └── Qwen 2.5 Coder 32B or R1-Distill-32B
│
├── Need reasoning chain? ─────────────► DeepSeek R1
│
├── Massive context? (1M+ tokens) ─────► Gemini 3.1 Pro or Llama 4 Scout
│
├── Code understanding? ───────────────► GPT-5.3-Codex or Claude Code
│
├── Research/deep analysis? ───────────► Claude Opus 4
│
├── Budget conscious? ─────────────────► DeepSeek (free tier) or local
│
└── General purpose? ──────────────────► Claude Sonnet 4 or GPT-5.2
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial release |
| 2.0 | Feb 2026 | Added Gemini 3.1 Pro, GPT-5.3-Codex, Llama 4, updated pricing |

---

**End of Guide**

*This guide will be updated as new models are released. Check for updates at the source repository.*

---

**License:** This guide is provided for educational purposes. Model names and trademarks belong to their respective owners.
