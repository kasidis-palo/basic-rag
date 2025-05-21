from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_chunks(text, chunk_size=1000, chunk_overlap=200) -> List[str]:
    """Split text into chunks using LangChain's RecursiveCharacterTextSplitter."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    return chunks
