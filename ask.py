import sys
from openai import OpenAI
from qdrant_client import QdrantClient
from constants import (
    OPENAI_URL,
    OPENAI_API_KEY,
    QDRANT_URL,
    QDRANT_PORT,
)

from rag import RAG

def ask(question: str):

    # เตรียม client สำหรับ OpenAI และ Qdrant
    ollama_client = OpenAI(base_url=OPENAI_URL, api_key=OPENAI_API_KEY)
    qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, prefer_grpc=True)

    # เรียกใช้ RAG
    rag = RAG(ollama_client, qdrant_client)
    response = rag.ask(question)

    print(f"\nResponse to query '{question}':\n\n {response}")
    
    return response

if __name__ == "__main__":

    # รับคำถามจาก command line
    if len(sys.argv) != 2:
        print("Usage: python ask.py <question>")
        sys.exit(1)
    question = sys.argv[1]

    # ถามเลย!
    ask(question)