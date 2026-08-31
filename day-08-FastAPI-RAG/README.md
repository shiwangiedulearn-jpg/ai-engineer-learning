ResearchRAG

A full-stack Retrieval-Augmented Generation (RAG) application that lets users upload research documents and ask questions about their content. Documents are extracted, chunked, embedded with Google's Gemini embedding model, stored in Qdrant Cloud, and retrieved to provide context for generated answers.

Features

Upload .txt, .pdf, and .docx documents

Automatic text extraction and chunking

Gemini gemini-embedding-001 embeddings

768-dimensional embeddings

Vector storage and similarity search with Qdrant Cloud

Retrieval filtered by selected document IDs

SHA-256 duplicate-file detection

Question answering over selected documents

Source names returned with answers

Delete documents and their vectors

FastAPI Swagger/OpenAPI documentation

React + TypeScript + Vite frontend

Production deployment with Render and Vercel

Architecture

React + Vite (Vercel)
        |
        | HTTP / JSON
        v
FastAPI Backend (Render)
      /   \
     /     \
 Gemini   Qdrant Cloud
Embedding   Vector Search
     \     /
      \   /
   Retrieved Context
        |
        v
  Gemini Generation
        |
        v
      Answer

How It Works

Upload - The user uploads a supported document.

Validation - The backend validates the extension and calculates a SHA-256 hash to detect duplicates.

Text Extraction - Text is extracted from TXT, PDF, or DOCX files.

Chunking - The extracted text is split into smaller chunks.

Embedding - Gemini gemini-embedding-001 converts chunks into 768-dimensional vectors.

Storage - Vectors and metadata (text, source, document_id, and chunk_id) are stored in Qdrant.

Question Embedding - A user's question is embedded with the same embedding model.

Retrieval - Qdrant performs cosine-similarity search and returns the most relevant chunks, optionally restricted to selected documents.

Generation - The retrieved context is passed to the generation component to produce the final answer.

Tech Stack

Backend

Python

FastAPI

Google Gemini API

Qdrant Cloud

NumPy

python-dotenv

Uvicorn

Frontend

React

TypeScript

Vite

Deployment

Frontend: Vercel

Backend: Render

Vector database: Qdrant Cloud

Project Structure

day-08-FastAPI-RAG/
├── main.py
├── requirements.txt
├── .env
├── rag/
│   ├── documents.py
│   ├── embeddings.py
│   ├── generation.py
│   └── retrieval.py
├── data/
│   └── uploads/
└── frontend/
    ├── src/
    ├── public/
    ├── package.json
    ├── vite.config.*
    └── ...

Environment Variables

Backend

Create a .env file:

GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key

Frontend

For Vite, configure:

VITE_API_BASE_URL=https://your-render-backend-url

For local development:

VITE_API_BASE_URL=http://127.0.0.1:8000

Never commit .env files or API keys to GitHub.

Run Locally

Backend

cd day-08-FastAPI-RAG
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

Frontend

cd frontend
npm install
npm run dev

The Vite development server normally runs at:

http://localhost:5173

Set VITE_API_BASE_URL to the local FastAPI URL.

API Endpoints

Method

Endpoint

Purpose

GET

/

Health check

GET

/documents

List uploaded documents

POST

/upload

Upload and index a document

POST

/ask

Ask a question using retrieved context

DELETE

/document/{document_id}

Delete a document and its vectors

Interactive documentation is available at /docs.

Deployment

Backend — Render

The backend is deployed as a Render Web Service.

Root Directory: day-08-FastAPI-RAG
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT

Gemini and Qdrant credentials are configured as Render environment variables.

Frontend — Vercel

The frontend is deployed from:

day-08-FastAPI-RAG/frontend

Typical Vite settings:

Build Command: npm run build
Output Directory: dist

The production frontend uses VITE_API_BASE_URL pointing to the Render backend. FastAPI CORS is configured to allow the deployed Vercel frontend origin.

Duplicate Handling

Before indexing an uploaded file, the backend calculates its SHA-256 hash. If the same file already exists, the API returns:

409 Conflict

This prevents duplicate indexing and unnecessary embedding calls.

Important Notes

Qdrant uses cosine similarity for retrieval.

The embedding dimension must match between Gemini embeddings and the Qdrant collection.

Uploaded files are stored under data/uploads.

Production deployments should use persistent storage if uploaded files need to survive service restarts or redeployments.

Keep all API credentials in environment variables.

Future Improvements

Conversation history

Authentication and user-specific document collections

Persistent production file storage

Streaming answers

Better chunking and metadata

Source-level citations in answers

Retrieval and answer-quality evaluation

Background processing for large documents

Author

Built as a hands-on AI/ML project demonstrating an end-to-end RAG pipeline using FastAPI, Gemini, Qdrant Cloud, React, Vite, Render, and Vercel.