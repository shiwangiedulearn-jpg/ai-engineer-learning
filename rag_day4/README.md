# Day 4 — RAG Retrieval

## What I learned

- Document chunking
- Chunk overlap
- Embedding chunks
- Query embeddings
- Cosine similarity
- Top-k retrieval

## Built

A basic retrieval pipeline that:

1. Splits documents into chunks
2. Generates embeddings
3. Embeds the user query
4. Calculates similarity
5. Retrieves the most relevant chunks

## Architecture

Document
↓
Chunking
↓
Embeddings
↓
Vector similarity
↓
Top-k retrieval