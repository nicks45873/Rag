# AI Assistance & Methodology Audit Log (AI_USAGE.md)

This log documents how AI technologies were leveraged during the design, development, prompt engineering, and code verification of the **RAG-based AI Enterprise Assistant**.

---

## 1. System Prompt Engineering Methodology

To ensure strict zero-hallucination grounded responses, system prompts were engineered with four explicit constraints:

```text
You are an enterprise AI assistant specializing in corporate documents, HR policies, and technical guidelines.
Strict Instructions:
1. Answer the user's question using ONLY the provided context blocks below.
2. For EVERY key claim or policy detail in your answer, cite the source using the exact format: [Doc: <filename>, Page: <page_num>].
3. If the context does not contain enough information to answer truthfully, state: 'The provided documents do not contain sufficient information to answer this query.'
4. Do NOT hallucinate or use external knowledge not present in the context.
```

### Key Guardrail Elements:
- **Scope Boundary**: Forces the LLM to restrict context solely to retrieved chunks.
- **Structured Citation Injunction**: Mandates inline citation tags corresponding to metadata records.
- **Explicit Fallback Directive**: Prevents guessing when documents lack context.

---

## 2. AI Leveraged in Architecture & Engineering

- **System Architecture Formulation**: AI was utilized to draft modular boundaries separating Document Processing, Semantic Chunking, Vector Storage, Similarity Search, and API endpoints.
- **Grounded Offline Extractor Engine**: Developed an offline extraction algorithm using AI-guided sentence scoring to deliver instant grounded answers when cloud LLM APIs are unavailable.
- **Automated Test Generation**: AI assistance was used to construct unit and integration test fixtures covering edge cases (corrupt files, empty queries, confidence thresholding).

---

## 3. Code Audit & Quality Compliance

- **Code Review**: All generated Python modules (`FastAPI`, `Streamlit`, `ChromaDB`, `SentenceTransformers`) were audited for syntax correctness, type hint accuracy, and explicit error handling.
- **Dependency Hygiene**: Checked package bounds and eliminated version conflicts between `starlette`, `fastapi`, and `streamlit`.
- **Security & Privacy Audit**: Verified that API keys and vector database storage operate locally without inadvertent data exposure.
