from sentence_transformers import SentenceTransformer
model= SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model loaded")

def create_embeddings(chunks):
    chunk_texts= [chunk["text"] for chunk in chunks]

    print("no. of chunks: ", len(chunks))
    print("no. of chunk texts: ",len(chunk_texts))
    print("Type of chunk texts", type(chunk_texts))
    
    embeddings= model.encode(
        chunk_texts,
        convert_to_numpy= True,
        normalize_embeddings= True
    )

    print("Embedding shape: ", embeddings.shape)
    return embeddings

def create_query_embedding(query):
    query_embedding= model.encode(
        query,
        convert_to_numpy= True,
        normalize_embeddings= True
    )
    return query_embedding