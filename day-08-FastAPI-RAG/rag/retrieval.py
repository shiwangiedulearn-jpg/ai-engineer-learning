from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

qdrant= QdrantClient(path= "qdrant_data")
print("Qdrant connected")

collection_name= "medisense_knowledge"
def create_collection(embedding_dimension):
    qdrant.recreate_collection(
        collection_name= collection_name,
        vectors_config= VectorParams(
            size= embedding_dimension,
            distance= Distance.COSINE
        )
    )
    print("Qdrant collection created")

def store_embeddings(chunks, embeddings):
    points=[]
    for i, (chunk, embedding) in enumerate (zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=i,
                vector=embedding.tolist(),
                payload={
                    "text":chunk["text"],
                    "source": chunk["source"]
                }
            )
        )

    qdrant.upsert(
        collection_name= collection_name,
        points=points
    )
    print("embedding stored in Qdrant ", len(points))


def search_qdrant(query_embedding, top_k=3):
    results= qdrant.query_points(
        collection_name= collection_name,
        query= query_embedding.tolist(),
        limit= top_k
    )
    return results.points