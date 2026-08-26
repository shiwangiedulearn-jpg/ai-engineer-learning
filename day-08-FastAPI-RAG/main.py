from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
import os

from rag.embeddings import create_embeddings, create_query_embedding
from rag.retrieval import create_collection, store_embeddings, search_qdrant
from rag.generation import generate_answer
from rag.documents import load_documents, create_chunks

app= FastAPI()

load_dotenv()
client= genai.Client(
    api_key= os.getenv("GEMINI_API_KEY")
)
print("Gemini client initialized")

documents= load_documents()
#chunking----------------------------------------------------------------------

chunks= create_chunks(documents)

# embedding------------------------------------------------------------------


embeddings = create_embeddings(chunks)

#qdrant client
create_collection(embeddings.shape[-1])

store_embeddings(chunks, embeddings)

#search relevnt chunks---------------------------------------------------------------------

def search_documents(query, top_k=3):
    query_embedding= create_query_embedding(query)
    results= search_qdrant(
        query_embedding,
        top_k
    )
    return results

test_query= "What is LDL cholestrol?"
results= search_documents(test_query)
print("\nSearch result")
for result in results:
    print("\nScores: ", result.score)
    print("Source: ", result.payload["source"])
    print("Text: ", result.payload["text"][:200])

 #gemini answer------------------------------------------------------------------
answer= generate_answer(client,test_query, results)
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
    answer = generate_answer(client,query, results)
    sources= list({
        result.payload["source"]
        for result in results
    })
    return{
        "question": query,
        "answer": answer,
        "sources": sources
    }


