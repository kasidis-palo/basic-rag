from openai import OpenAI
from qdrant_client import QdrantClient
from constants import (
    LLM_MODEL, 
    EMBEDDING_MODEL, 
    COLLECTION_NAME,
)

class RAG:
    def __init__(self, openai_client: OpenAI, qdrant_client: QdrantClient):
        self.openai_client = openai_client
        self.qdrant_client = qdrant_client

    # function เพื่่อค้นหาเอกสารที่เกี่ยวข้องจากฐานข้อมูล
    def get_relevant_documents(self, query: str, limit=5):
        # เอา prompt (query) ไปสร้าง embedding
        query_embedding = self.openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query
        ).data[0].embedding
        
        # เอา vector ที่ได้ไปค้นหาในฐานข้อมูล
        search_results = self.qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=limit
        )
        
        # เอาข้อมูลที่ได้จากการค้นหา (search results) มาเก็บใน context_texts
        context_texts = [hit.payload["text"] for hit in search_results.points]
        return context_texts

    # function สำหรับถาม RAG ของเรา
    def ask(self, query: str) -> str:
        # ค้นหาเอกสารที่เกี่ยวข้องจากฐานข้อมูล
        context_docs = self.get_relevant_documents(query)
        
        # เอา context_docs มาต่อกัน
        context_text = "\n\n".join(context_docs)
        
        # สร้าง prompt สำหรับถาม LLM
        prompt = f"""
            You are an expert on the rheology of cat. Answer the following question using ONLY the information in the context. If the answer is not in the context, say "I don't know".
            Do not mention the context in your answer.

            CONTEXT INFORMATION: {context_text}
            USER QUESTION: {query}
            """

        # ถาม LLM ของเราเลย!
        response = self.openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        return response.choices[0].message.content
