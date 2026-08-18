# Day 5 — End-to-End RAG

Built a basic **Retrieval-Augmented Generation (RAG)** pipeline using Python, Sentence Transformers, Scikit-learn, and the Gemini API.

## 🔄 Pipeline

```text
User Query
    ↓
Query Embedding
    ↓
Semantic Retrieval
    ↓
Top-K Relevant Chunks
    ↓
Context Construction
    ↓
Gemini LLM
    ↓
Grounded Answer