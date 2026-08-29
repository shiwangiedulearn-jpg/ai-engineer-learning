from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
import uuid
from dotenv import load_dotenv
import os

load_dotenv()
qdrant= QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
print("Qdrant connected")

collection_name= "research_knowledge"
def create_collection(embedding_dimension):

    collections = qdrant.get_collections().collections

    existing_collections = [
        collection.name for collection in collections
    ]

    if collection_name not in existing_collections:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_dimension,
                distance=Distance.COSINE
            )
        )
        print("Qdrant collection created")
    else:
        print("Qdrant collection already exists")

    qdrant.create_payload_index(
        collection_name=collection_name,
        field_name="document_id",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print("document_id index ready")

def store_embeddings(chunks, embeddings, document_id):
    points=[]
    for i, (chunk, embedding) in enumerate (zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id= str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "text":chunk["text"],
                    "source": chunk["source"],
                    "document_id": document_id,
                    "chunk_id": i
                }
            )
        )

    qdrant.upsert(
        collection_name= collection_name,
        points=points
    )
    print("embedding stored in Qdrant ", len(points))


def search_qdrant(query_embedding, document_ids=None, top_k=3):
    query_filter= None
    if document_ids:
        query_filter= Filter(
            should=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
                for document_id in document_ids
            ]
        )
    results = qdrant.query_points(
        collection_name=collection_name,
        query=query_embedding.tolist(),
        query_filter=query_filter,
        limit=top_k
    )

    return results.points

def delete_document(document_id):
    qdrant.delete(
        collection_name= collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )
    print("Deleted the document from Qdrant: ", document_id)

def document_exists(document_id):
    results = qdrant.count(
        collection_name=collection_name,
        count_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )

    return results.count > 0