from google import genai
from google.genai import types
import os
import numpy as np

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

print("Gemini embedding client initialized")


def create_embeddings(chunks):
    chunk_texts = [chunk["text"] for chunk in chunks]

    print("No. of chunks:", len(chunks))
    print("No. of chunk texts:", len(chunk_texts))

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=chunk_texts,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    embeddings = np.array(
        [embedding.values for embedding in result.embeddings]
    )

    print("Embedding shape:", embeddings.shape)

    return embeddings


def create_query_embedding(query):
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSION
        )
    )

    return np.array(result.embeddings[0].values)


def get_embedding_dimension():
    return EMBEDDING_DIMENSION