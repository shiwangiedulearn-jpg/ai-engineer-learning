from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os
import hashlib
from pathlib import Path
import uuid

from rag.embeddings import create_embeddings, create_query_embedding, get_embedding_dimension
from rag.retrieval import create_collection, store_embeddings, search_qdrant, delete_document, document_exists
from rag.generation import generate_answer
from rag.documents import extract_text, load_documents, create_chunks

app= FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://researchrag-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()
client= genai.Client(
    api_key= os.getenv("GEMINI_API_KEY")
)
print("Gemini client initialized")

documents= load_documents()
embedding_dimension= get_embedding_dimension()

#qdrant client
create_collection(embedding_dimension)
#to avaoid duplicates
for document in documents:

    document_id = document["source"]

    if document_exists(document_id):
        print("Already indexed:", document["source"])
        continue

    document_chunks = create_chunks([document])
    document_embeddings = create_embeddings(document_chunks)

    store_embeddings(
        document_chunks,
        document_embeddings,
        document_id
    )

#search relevnt chunks---------------------------------------------------------------------

def search_documents(query, document_ids, top_k=3):

    query_embedding = create_query_embedding(query)

    results = search_qdrant(
        query_embedding,
        document_ids,
        top_k
    )

    return results

class QuestionRequest(BaseModel):
    question: str
    document_ids: list[str]=[]

def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    allowed_extensions = [".txt", ".pdf", ".docx"]

    if Path(file.filename).suffix.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a txt, PDF, or DOCX file."
        )

    filename = Path(file.filename).name

    # Temporarily save the uploaded file
    temp_path = UPLOAD_DIR / f"temp_{filename}"

    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    # Calculate hash of uploaded file
    file_hash = calculate_file_hash(temp_path)

    # Check existing files for duplicate
    for existing_file in UPLOAD_DIR.iterdir():

        if not existing_file.is_file():
            continue

        if existing_file.name.startswith("temp_"):
            continue

        if calculate_file_hash(existing_file) == file_hash:
            temp_path.unlink(missing_ok=True)

            raise HTTPException(
                status_code=409,
                detail=f"Document already exists: {existing_file.name}"
            )

    # Create ID only after confirming it is not a duplicate
    document_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{document_id}_{filename}"

    temp_path.rename(file_path)

    try:
        text = extract_text(file_path)
    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Could not process the uploaded document"
        )
    if not text or not text.strip():
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from document"
        )
    document = {
        "text": text,
        "source": filename,
    }
    chunks = create_chunks([document])
    embeddings = create_embeddings(chunks)
    store_embeddings(
        chunks,
        embeddings,
        document_id
    )
    return {
        "document_id": document_id,
        "filename": filename,
        "chunks_created": len(chunks),
        "message": "File received successfully"
    }

@app.get("/")
def home():
    return{"message":"ResearchRAG RAG API is running!"}
@app.get("/documents")
def get_documents():
    documents=[]
    for file_path in UPLOAD_DIR.iterdir():
        if not file_path.is_file():
            continue
        filename= file_path.name
        document_id= filename.split("_",1)[0]
        documents.append({
            "document_id": document_id,
            "filename":filename.split("_",1)[1]
        })
    return{
        "documents": documents
    }

@app.delete("/document/{document_id}")
def delete_uploaded_document(document_id: str):
    files = list(UPLOAD_DIR.glob(f"{document_id}_*"))
    if not files:
        raise HTTPException(
            status_code=404,
            detail= "Document not found"
        )
    delete_document(document_id)
    for file_path in files:
        file_path.unlink()
    return{
        "document_ids": document_id,
        "filename": files[0].name,
        "message": "Document deleted successfully"
    }

@app.post("/ask")
def ask_question(request: QuestionRequest):
    query=request.question
    document_ids= request.document_ids
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )
    if document_ids:
        for document_id in document_ids:
            files = list(UPLOAD_DIR.glob(f"{document_id}_*"))

            if not files:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document not found: {document_id}"
                )
    results= search_documents(query, document_ids)
    if not results:
        return{
            "question": query,
            "document_ids": document_ids,
            "answer": "No information was found in selected document.",
            "source":[]
        }

    answer = generate_answer(client, query, results)
    sources= list({
        result.payload["source"]
        for result in results
    })
    
    return{
        "question": query,
        "document_ids": document_ids,
        "answer": answer,
        "sources": sources
    }


