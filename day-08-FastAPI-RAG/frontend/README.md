# ResearchRAG Frontend

A standalone React + Vite frontend for the ResearchRAG FastAPI backend.

## Run locally

1. Install Node.js.
2. Copy `.env.example` to `.env`.
3. Make sure FastAPI is running at `http://127.0.0.1:8000`.
4. Run:

```bash
npm install
npm run dev
```

Open the local Vite URL shown in the terminal.

## Backend endpoints

The frontend uses:

- `POST /upload`
- `GET /documents`
- `POST /ask`
- `DELETE /document/{document_id}`

The frontend never calls Gemini directly and never asks the user to enter document IDs.
