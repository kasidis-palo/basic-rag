import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from qdrant_client import QdrantClient
from openai import OpenAI

from rag import RAG
from constants import OPENAI_API_KEY, OPENAI_URL, QDRANT_PORT, QDRANT_URL
from evaluation.utils.llm_utils import LLMEvaluation
from evaluation.utils.document_utils import load_pdf_as_text_pages
from evaluation.utils.file_utils import write_jsonl_file


SOURCE_PDF_PATH = "on-the-rheology-of-cats.pdf"
OUTPUT_DIR = "evaluation/data/qa_pairs/"
OUTPUT_FILE_NAME = "qa_pairs.jsonl"
QUERY_PER_PAGE = 3  # จำนวนคู่คำถาม-คำตอบที่จะสร้างต่อหน้า

def prepare_qa_pairs():
    
    pdf_path = SOURCE_PDF_PATH
    
    # เริ่มต้น OpenAI client
    ollama_client = OpenAI(base_url=OPENAI_URL, api_key=OPENAI_API_KEY)
    
    
    # เริ่มต้น Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, prefer_grpc=True)
    
    # เริ่มต้นระบบ RAG
    rag_system = RAG(ollama_client, qdrant_client)
    
    llm_evaluator = LLMEvaluation(ollama_client, rag_system)
    
    # โหลดไฟล์ PDF เป็นข้อความและแบ่งเป็นหน้าจาก load_pdf_as_text_pages
    pages = load_pdf_as_text_pages(pdf_path)
    
    # รันเพื่อสร้างคู่คำถาม-คำตอบตามหน้าด้วยฟังก์ชัน generate_qa_pair ที่ตอบกลับเป็น QAPair
    all_qa_pairs = []
    
    # รันจนกว่าจะประมวลผลหน้าทั้งหมดเสร็จ
    for page_num, page_text in enumerate(pages):
        print(f"Processing page {page_num + 1}/{len(pages)}...")
        
        # สร้างคู่คำถาม-คำตอบสำหรับหน้านี้ (ส่งคืนเป็นลิสต์)
        qa_pairs = llm_evaluator.generate_qa_pair(page_text, QUERY_PER_PAGE)
        
        if qa_pairs:
            all_qa_pairs.extend(qa_pairs)
    
    # เขียนคู่คำถาม-คำตอบทั้งหมดลงในไฟล์ JSONL
    output_file_path = write_jsonl_file(OUTPUT_DIR, OUTPUT_FILE_NAME, [qa.__dict__ for qa in all_qa_pairs])
    print(f"All QA pairs written to {output_file_path}")


if __name__ == "__main__":
    prepare_qa_pairs()
    
    
    
    
     
  
     
     
