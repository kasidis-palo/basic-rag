from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams

def setup_qdrant_collection(client: QdrantClient, collection_name: str, embeddings):
    
    # เช็คว่ามี collection ที่ชื่อ COLLECTION_NAME อยู่แล้วไหม ถ้ามี ให้ลบออก
    existing_collections = map(lambda collection: collection.name, client.get_collections().collections)
    if collection_name in existing_collections:
        print(f"Collection {collection_name} already exists. Deleting it...")
        client.delete_collection(collection_name)

    # สร้าง collection ใหม่
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=len(embeddings[0].vector),
            distance=Distance.COSINE
        )
    )

    # เก็บข้อมูลลงใน collection
    print(f"Saving results to vector database {collection_name}...")
    client.upsert(
        collection_name=collection_name,
        points=embeddings
    )

