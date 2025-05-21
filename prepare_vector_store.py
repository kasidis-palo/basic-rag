from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.http.models import VectorParams, Distance

from pdf_utils import extract_text_from_pdf
from chunk_utils import create_chunks
from ollama_utils import generate_embeddings
from qdrant_utils import setup_qdrant_collection
from constants import (
    OPENAI_URL,
    OPENAI_API_KEY,
    COLLECTION_NAME,
    QDRANT_URL,
    QDRANT_PORT,
)

def prepare_vector_store():

    # เตรียม client สำหรับ OpenAI และ Qdrant
    ollama_client = OpenAI(base_url=OPENAI_URL, api_key=OPENAI_API_KEY)
    qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, prefer_grpc=True)

    # อ่านไฟล์ PDF
    pdf_path = "on-the-rheology-of-cats.pdf"
    text = extract_text_from_pdf(pdf_path)

    # สร้าง chunks จากข้อความ
    chunks = create_chunks(text)

    # เอา chunks แต่ละตัวไปทำ embedding
    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunk)}: {chunk[:30]}...")
        embedding = generate_embeddings(ollama_client, chunk)
        embeddings.append(PointStruct(
            id=i,
            vector=embedding,
            payload={
                "text": chunk
            },
        ))

    # สร้าง collection และเก็บข้อมูล
    setup_qdrant_collection(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings
    )

if __name__ == "__main__":
    prepare_vector_store()