

import sys
import os
import glob
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from evaluation.utils.file_utils import read_jsonl_file

INPUT_DIR = "evaluation/data/evaluation/"
OUTPUT_DIR = "evaluation/data/report/"
OUTPUT_FILE_NAME = "evaluation_report.md"


def generate_evaluation_report():
    
    # ค้นหาไฟล์ผลการประเมินล่าสุด
    evaluation_files = glob.glob(os.path.join(INPUT_DIR, "*_llm_judge_evaluation_results.jsonl"))
    
    if not evaluation_files:
        print(f"No evaluation files found in {INPUT_DIR}")
        return
    
    # ดึงไฟล์ล่าสุด (ตามเวลาที่แก้ไข)
    latest_file = max(evaluation_files, key=os.path.getmtime)
    print(f"Using evaluation file: {latest_file}")
    
    # อ่านผลการประเมิน
    evaluation_results = read_jsonl_file(latest_file)
    print(f"Loaded {len(evaluation_results)} evaluation results")
    
    # แยกชื่อไฟล์สำหรับชื่อรายงานที่ไม่ซ้ำ
    input_filename = os.path.basename(latest_file)
    timestamp_part = input_filename.split('_')[0]  # แยก timestamp จากชื่อไฟล์
    unique_report_name = f"{timestamp_part}_evaluation_report.md"
    
    # คำนวณสถิติสรุป
    scores = [result['score'] for result in evaluation_results]
    avg_score = sum(scores) / len(scores) if scores else 0
    score_distribution = {}
    for score in set(scores):
        score_distribution[score] = scores.count(score)
    
    # สร้างไดเร็กทอรีเอาต์พุตหากไม่มีอยู่
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # สร้างรายงาน Markdown
    report_content = generate_markdown_report(evaluation_results, avg_score, score_distribution)
    
    # เขียนรายงานลงไฟล์
    output_path = os.path.join(OUTPUT_DIR, unique_report_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Evaluation report generated: {output_path}")
    print(f"Summary: {len(evaluation_results)} questions evaluated, average score: {avg_score:.2f}/5")
    
    return output_path


def generate_markdown_report(evaluation_results, avg_score, score_distribution):
    """สร้างรายงาน Markdown ที่เรียบง่ายและชัดเจนจากผลการประเมิน"""
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_questions = len(evaluation_results)
    
    report = f"""# RAG System Evaluation Report

Generated: {current_time}

## Summary
- **Questions Tested:** {total_questions}
- **Average Score:** {avg_score:.1f}/5

## Results
"""
    
    # Simple score breakdown
    for score in sorted(score_distribution.keys(), reverse=True):
        count = score_distribution[score]
        report += f"- **{score}/5**: {count} questions\n"
    
    report += f"""
## Question Details

"""
    
    # รายละเอียดคำถามทีละข้อ
    for i, result in enumerate(evaluation_results, 1):
        # การใช้สีตามคะแนน
        score_emoji = {5: "🟢", 4: "🟡", 3: "🟠", 2: "🔴", 1: "⚫"}
        emoji = score_emoji.get(result['score'], "⚪")
        
        report += f"""---
### {emoji} Q{i}: {result['question']}

**📊 Score: `{result['score']}/5`**

**✅ Expected Answer:**
> {result['answer']}

**🤖 LLM Answer:**
> {result['llmAnswer']}

**⚖️ Judge Reasoning:**
> {result['reason']}

"""
    
    # สรุปเรียบง่าย
    if avg_score >= 4:
        performance = "Excellent"
    elif avg_score >= 3:
        performance = "Good"
    elif avg_score >= 2:
        performance = "Fair"
    else:
        performance = "Needs Improvement"
    
    report += f"""## Conclusion
The RAG system performance is **{performance}** with an average score of {avg_score:.1f}/5.
"""
    
    return report
    








if __name__ == "__main__":
    generate_evaluation_report()
    