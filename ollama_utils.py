from openai import OpenAI
from typing import List, Dict
from constants import EMBEDDING_MODEL

def generate_embeddings(client: OpenAI, text: str) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding
