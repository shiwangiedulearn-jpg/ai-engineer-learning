from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct #is a structure qdrant uses to represent a point in the vector space, including its ID, vector, and optional payload.
from google import genai
from dotenv import load_dotenv
import os

app= FastAPI()

load_dotenv()
client= genai.Client(
    api_key= os.getenv("GEMINI_API_KEY")
)
print("Gemini client initialized")

data_folder = Path("data")
documents = []
for file_path in data_folder.glob('*.txt'):
    text= file_path.read_text(encoding= "utf-8")
    documents.append({
        "text": text,
        "source": file_path.name
    })
print("Documents loaded: ", len(documents))
for document in documents:
    print("source: ", document["source"])
#chunking----------------------------------------------------------------------

chunks=[]
chunk_size=500
overlap=100
for document in documents:
    text= document["text"]
    source= document["source"]
    start=0
    while start< len(text):
        end= start+ chunk_size
        chunk_texts= text[start:end]
        chunks.append({
            "text": chunk_texts,
            "source": source
        })
        start= end-overlap

print("Total chunks:", len(chunks))
for chunk in chunks[:5]:
    print("\nSource:", chunk["source"])
    print("Text:", chunk["text"][:100])
# embedding------------------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded")

chunk_texts = [chunk["text"] for chunk in chunks]

print("Number of chunks:", len(chunks))
print("Number of chunk texts:", len(chunk_texts))
print("Type of chunk_texts:", type(chunk_texts))

if len(chunk_texts) > 0:
    print("Type of first chunk:", type(chunk_texts[0]))
    print("First chunk preview:", chunk_texts[0][:100])


embeddings = model.encode(
    chunk_texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

print("Embeddings shape:", embeddings.shape)

#qdrant client
qdrant= QdrantClient(path="qdrant_data")
print("Qdrant connected")

collection_name= "medisense_knowledge"
qdrant.recreate_collection(
    collection_name= collection_name,
    vectors_config=VectorParams(
        size= embeddings.shape[-1],
        distance= Distance.COSINE
    )
)
print("Qdrant collection created")

#storing embeddings---------------------------------------------------------------------

points= []
for i, (chunk,embedding) in enumerate(zip(chunks, embeddings)):
    points.append(
        PointStruct(
            id=i,
            vector= embedding.tolist(),
            payload={
                "text": chunk["text"],
                "source": chunk["source"]
            }
        )
    )
qdrant.upsert(
    collection_name= collection_name,
    points= points
)
print("Embeddings stored in Qdrant:",len(points))

#search relevnt chunks---------------------------------------------------------------------

def search_documents(query, top_k=3):
    query_embedding= model.encode(
        query,
        convert_to_numpy= True,
        normalize_embeddings= True
    )
    results= qdrant.query_points(
        collection_name= collection_name,
        query= query_embedding.tolist(),
        limit= top_k
    )
    return results.points

test_query= "What is LDL cholestrol?"
results= search_documents(test_query)
print("\nSearch result")
for result in results:
    print("\nScores: ", result.score)
    print("Source: ", result.payload["source"])
    print("Text: ", result.payload["text"][:200])

 #gemini answer------------------------------------------------------------------
def generate_answer(query, results):
    context= "\n\n".join(
        result.payload["text"]
        for result in results
    )
    print("\n========== CONTEXT SENT TO GEMINI ==========")
    print(context)
    print("============================================\n")
    prompt=f"""
    You are a medical infomation assistant.
    Answer the user's question using only the information provided in the context below.
    If the context doesnot contain enough information to answer the wuestion just say:
    "I dont have enough information in the provided documents."
    Donot invent medical facts.
    Context:
    {context}

    User question:
    {query}
    Answer:
    """
    response= client.models.generate_content(
        model= "gemini-3.6-flash",
        contents=prompt
    )
    return response.text

answer= generate_answer(test_query, results)
print("\nGemini answer:")
print(answer)

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return{"message":"MediSense RAG API is running!"}

@app.post("/ask")
def ask_question(request: QuestionRequest):
    query=request.question
    results= search_documents(query)
    answer = generate_answer(query, results)
    sources= list({
        result.payload["source"]
        for result in results
    })
    return{
        "question": query,
        "answer": answer,
        "sources": sources
    }


