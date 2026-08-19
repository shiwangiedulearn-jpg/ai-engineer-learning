# Day 4 — RAG Retrieval

Built the **retrieval component of a RAG system** using document chunking, embeddings, and semantic similarity search.

## 🔄 Pipeline

```text
Medical Documents
        ↓
Text Chunking
        ↓
Chunk Embeddings
        ↓
User Query
        ↓
Query Embedding
        ↓
Cosine Similarity
        ↓
Top-K Relevant Chunks