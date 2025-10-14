import sys
import os

from qdrant_client import QdrantClient
from openai import OpenAI

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import root-level modules
from rag import RAG
from constants import OPENAI_API_KEY, OPENAI_URL, QDRANT_PORT, QDRANT_URL

# Import simple_evaluation modules
from evaluation.utils.llm_utils import LLMEvaluation
from evaluation.models.qa_pairs_model import QAPairLLMAnswer
from evaluation.utils.file_utils import write_jsonl_file, read_jsonl_file, get_unique_name_for_file_name


LLM_ANSWERS_QA_PAIRS_DIR = "evaluation/data/llm_answers/"
LLM_ANSWERS_QA_PAIRS_FILE_NAME = "llm_answers_qa_pairs.jsonl"
OUTPUT_DIR = "evaluation/data/evaluation/"
OUTPUT_FILE_NAME = "llm_judge_evaluation_results.jsonl"


def evaluate_llm_as_a_judge():
    
    # เริ่มต้น OpenAI client
    ollama_client = OpenAI(base_url=OPENAI_URL, api_key=OPENAI_API_KEY)
        # เริ่มต้น Qdrant client
    qdrant_client = QdrantClient(url=QDRANT_URL, port=QDRANT_PORT, prefer_grpc=True)
    
    # เริ่มต้นระบบ RAG
    rag_system = RAG(ollama_client, qdrant_client)
    
    llm_evaluator = LLMEvaluation(ollama_client, rag_system)
    
    # โหลดคู่คำถาม-คำตอบของ LLM
    input_file_path = os.path.join(LLM_ANSWERS_QA_PAIRS_DIR, LLM_ANSWERS_QA_PAIRS_FILE_NAME)
    
    # ตรวจสอบว่าไฟล์อินพุตมีอยู่หรือไม่
    if not os.path.exists(input_file_path):
        print(f"Input file not found: {input_file_path}")
        return
    
    # โหลดไฟล์ JSONL
    llm_answers_data = read_jsonl_file(input_file_path)
    print(f"Loaded {len(llm_answers_data)} LLM answers for evaluation")
    
    # ประมวลผลแต่ละไอเทมและรวบรวมผลการประเมิน
    evaluation_results = []
    
    for i, item in enumerate(llm_answers_data):
        print(f"Evaluating item {i+1}/{len(llm_answers_data)}: {item['question'][:50]}...")
        
        # สร้าง QAPairLLMAnswer object จากข้อมูลที่โหลดมา
        qa_pair_llm_answer = QAPairLLMAnswer(
            question=item['question'],
            answer=item['answer'],
            llmAnswer=item['llmAnswer']
        )
        
        # ประเมินคำตอบของ LLM
        evaluation_result = llm_evaluator.evaluate_llm_answer(qa_pair_llm_answer)
        
        # แปลงเป็น dictionary สำหรับเอาต์พุต JSONL
        result_dict = {
            "question": evaluation_result.question,
            "answer": evaluation_result.answer,
            "llmAnswer": evaluation_result.llmAnswer,
            "score": evaluation_result.score,
            "reason": evaluation_result.reason
        }
        
        evaluation_results.append(result_dict)
        print(f"Score: {evaluation_result.score}/5")
        print(f"Reason: {evaluation_result.reason[:100]}...")
    
    # สร้างชื่อไฟล์เอาต์พุตที่ไม่ซ้ำ
    unique_output_file_name = get_unique_name_for_file_name(OUTPUT_FILE_NAME)
    
    # เขียนผลการประเมินลงในไฟล์ JSONL ใหม่
    output_file_path = write_jsonl_file(OUTPUT_DIR, unique_output_file_name, evaluation_results)
    print(f"Evaluation completed! Results saved to: {output_file_path}")
    
    # พิมพ์สถิติสรุป
    scores = [result['score'] for result in evaluation_results]
    avg_score = sum(scores) / len(scores) if scores else 0
    print(f"\nEvaluation Summary:")
    print(f"Total questions evaluated: {len(evaluation_results)}")
    print(f"Average score: {avg_score:.2f}/5")
    print(f"Score distribution: {dict(zip(*zip(*[(score, scores.count(score)) for score in set(scores)])))}")
   

if __name__ == "__main__":
    evaluate_llm_as_a_judge()