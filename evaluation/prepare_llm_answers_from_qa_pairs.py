import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from qdrant_client import QdrantClient
from constants import OPENAI_API_KEY, OPENAI_URL, QDRANT_PORT, QDRANT_URL
from evaluation.utils.llm_utils import LLMEvaluation
from evaluation.models.qa_pairs_model import QAPair
from evaluation.utils.file_utils import write_jsonl_file, read_jsonl_file
from rag import RAG


DATASET_DIR = "evaluation/data/qa_pairs/"
DATASET_FILE_NAME = "qa_pairs.jsonl"
OUTPUT_DIR = "evaluation/data/llm_answers/"
OUTPUT_FILE_NAME = "llm_answers_qa_pairs.jsonl"

def prepare_llm_answers_from_qa_pairs():
    
    # เริ่มต้น OpenAI client
    ollama_client = OpenAI(base_url=OPENAI_URL, api_key=OPENAI_API_KEY)
    
    # เริ่มต้น Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, prefer_grpc=True)
    
    # เริ่มต้นระบบ RAG
    rag_system = RAG(ollama_client, qdrant_client)
    
    # เริ่มต้น LLM evaluator ด้วยระบบ RAG
    llm_evaluator = LLMEvaluation(ollama_client, rag_system)
    
    # โหลดคู่คำถาม-คำตอบจากไฟล์ jsonl
    qa_pairs_file_path = os.path.join(DATASET_DIR, DATASET_FILE_NAME)
    qa_pairs_data = read_jsonl_file(qa_pairs_file_path)
    
    # แปลงเป็น QAPair objects
    qa_pairs = [QAPair(**data) for data in qa_pairs_data]
    print(f"Loaded {len(qa_pairs)} QA pairs from {qa_pairs_file_path}")
    
    # รันลูปเพื่อสร้างคำตอบ LLM จากคู่คำถาม-คำตอบโดยใช้ระบบ RAG
    llm_answers = []
    
    for i, qa_pair in enumerate(qa_pairs):
        print(f"Processing QA pair {i + 1}/{len(qa_pairs)}: {qa_pair.question[:50]}...")
        
        # สร้างคำตอบ LLM โดยใช้ระบบ RAG (ไม่ต้องใช้พารามิเตอร์ document)
        llm_answer = llm_evaluator.generate_llm_answer(qa_pair)
        
        if llm_answer:
            llm_answers.append(llm_answer)
            print(f"Generated answer: {llm_answer.llmAnswer[:100]}...")
    
    # เขียน QAPairLLMAnswer ทั้งหมดลงในไฟล์ JSONL
    output_file_path = write_jsonl_file(OUTPUT_DIR, OUTPUT_FILE_NAME, [answer.__dict__ for answer in llm_answers])
    print(f"All LLM answers written to {output_file_path}")
    print(f"Total answers generated: {len(llm_answers)}")
    
    return llm_answers


if __name__ == "__main__":
    prepare_llm_answers_from_qa_pairs()