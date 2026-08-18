# Architectural Decision Log (DECISION_LOG.md)

This log documents the technical rationale behind key design, architectural, and framework choices made while building the **RAG-based AI Enterprise Assistant**.

---

## 1. Vector Database Selection: ChromaDB over FAISS Pure Index

### Decision:
Selected **ChromaDB** with persistent disk storage (`chromadb.PersistentClient`) and Cosine distance metric (`hnsw:space: cosine`).

### Rationale:
- **Rich Native Metadata Support**: Unlike raw FAISS indices which require external dictionary mappings to associate vector indices with document metadata (page numbers, section titles, file names), ChromaDB seamlessly handles document payloads, embeddings, and complex JSON metadata in a unified data model.
- **Persistence & Portability**: ChromaDB persists index state directly to SQLite/parquet files on disk (`./data/chroma_db`), ensuring that indexed enterprise documents survive application restarts without re-embedding.
- **Built-in Deletion & Filtering**: Enables targeted metadata filtering (`where={"doc_id": "..."}`) and single-command document removal (`delete(ids=...)`).

---

## 2. Text Chunking Strategy: Recursive Character Splitter with Metadata Tagging

### Decision:
Implemented `langchain_text_splitters.RecursiveCharacterTextSplitter` with `chunk_size=500` characters, `chunk_overlap=100` characters, and structural delimiters `["\n\n", "\n", ". ", "; ", " ", ""]`.

### Rationale:
- **Structural Integrity**: Hard token or character splitting without boundary awareness cuts sentences and paragraphs in half, degrading embedding quality. Recursive splitting preserves paragraph and sentence boundaries.
- **Context Overlap (100 chars)**: Overlapping chunks ensure that facts spanning chunk boundaries (e.g. policy conditions) are captured across adjacent vector representations.
- **Structural Metadata Attachment**: Every chunk is tagged with `doc_id`, `filename`, `page_num`, `section`, `chunk_index`, and `char_count` for precise citation tracing.

---

## 3. Embedding Model Selection: `all-MiniLM-L6-v2` via `SentenceTransformers`

### Decision:
Chosen `all-MiniLM-L6-v2` as the default local dense embedding model.

### Rationale:
- **Performance & Efficiency**: Outputs 384-dimensional normalized vectors with fast CPU inference time (~15ms per chunk).
- **Offline & Privacy-First**: Runs 100% locally without sending sensitive corporate documents to third-party cloud APIs.
- **Proven Quality**: High benchmarking scores on semantic textual similarity (STS) tasks.

---

## 4. Multi-LLM Provider Architecture & Offline Fallback Engine

### Decision:
Designed a pluggable `LLMService` supporting:
1. **Smart Grounded Extractor Engine (Default Offline Mode)**
2. **OpenAI GPT-4o / GPT-3.5**
3. **Ollama Local LLM**

### Rationale:
- **Zero-Dependency Quickstart**: Enterprises often evaluate software in restricted environments without immediate access to paid OpenAI API keys. The Smart Grounded Extractor guarantees 100% functional RAG execution out of the box.
- **Grounded Verification**: Eliminates hallucination risk by enforcing that answers originate strictly from retrieved text blocks.

---

## 5. UI & API Stack: FastAPI + Streamlit Dual-Layer Architecture

### Decision:
Built a decoupled **FastAPI** backend for core API endpoints and a high-aesthetic **Streamlit** dashboard for human interaction.

### Rationale:
- **FastAPI**: Provides OpenAPI/Swagger documentation, async support, pydantic request validation, and clean integration for third-party tools.
- **Streamlit**: Allows rapid deployment of an interactive enterprise dashboard featuring dynamic glassmorphic visual cards, live metrics, vector index inspector, and file upload dropzones.
