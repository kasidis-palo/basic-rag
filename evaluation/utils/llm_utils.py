from openai import OpenAI
from constants import LLM_MODEL
from evaluation.models.qa_pairs_model import QAPair, QAPairList, QAPairLLMAnswer, QAPairLLMEvaluation
from rag import RAG

class LLMEvaluation:
	def __init__(self, openai_client: OpenAI, rag_system: RAG):
		self.openai_client = openai_client
		self.rag_system = rag_system

	# ฟังก์ชันสำหรับสร้างคำถามและคำตอบจาก context โดยใช้ LLM
	def generate_qa_pair(self, context: str, max_queries = 2) -> list[QAPair]:
		prompt = f"""
			You are an expert assistant in LLM evaluation (In the rheology of cat area).
			Given the following context, generate up to {max_queries} question(s) and their answer(s) based ONLY on the information in the context.
			
			REQUIREMENTS:
			1. Generate diverse, non-duplicating questions that cover different aspects of the context
			2. Mix difficulty levels:
			   - Easy: Direct factual questions that can be answered word-for-word from the context
			   - Medium: Questions requiring understanding and paraphrasing of concepts
			   - Hard: Questions requiring inference, analysis, or connecting multiple pieces of information
			3. Ensure each question tests different knowledge areas from the context
			4. Avoid repetitive question patterns or similar phrasings
			5. Make questions specific and answerable only from the given context
			6. Include questions that test both explicit information and implicit understanding

			CONTEXT: {context}
		"""
	
		completion = self.openai_client.chat.completions.parse(
			model=LLM_MODEL,
			messages=[{"role": "user", "content": prompt}],
			temperature=0.2,
			response_format=QAPairList
		)
		
		message = completion.choices[0].message

		return message.parsed.qa_pairs

	# ฟังก์ชันสำหรับสร้าง คำตอบจาก LLM โดยใช้ RAG system
	def generate_llm_answer(self, qaPair: QAPair) -> QAPairLLMAnswer:
		if self.rag_system is None:
			raise ValueError("RAG system must be provided in constructor to use this function")
		
		# Use RAG system to get answer
		llm_answer = self.rag_system.ask(qaPair.question)
		
		response = QAPairLLMAnswer(
			question=qaPair.question,
			answer=qaPair.answer, 
			llmAnswer=llm_answer
		)
		return response

	# ฟังก์ชันสำหรับให้คะแนนคำตอบจาก LLM โดยใช้ LLM
	def evaluate_llm_answer(self, qaPairLLMAnswer: QAPairLLMAnswer) -> QAPairLLMEvaluation:
	   # If is answer over scope but cover context in expected answer is ok can give score > 4-5
     
       # สร้าง prompt สำหรับการให้คะแนน	
		prompt = f"""
			You are an expert assistant in LLM evaluation (In the rheology of cat area).
			Compare the LLM answer to the reference answer and score similarity (0=not at all, 5=perfect).
      
            SCORING GUIDELINES:
            - **PRIORITY**: Check if LLM answer contains or covers the key content from the expected answer first
            - If the LLM answer goes beyond the scope but still covers all key context from the expected answer, it MUST receive a high score (4-5)
            - Focus on content accuracy and completeness rather than exact matching
            - More detailed/comprehensive answers that include the expected content should score higher, not lower
            - Only use "Completely Wrong" if the answer is factually incorrect or completely unrelated
            
            EVALUATION STEPS:
            1. First identify if the LLM answer contains the core content from the reference answer
            2. Then assess if additional information is accurate and relevant
            3. Score based on completeness and accuracy, not brevity
            
            REASON CATEGORIES:
            - "Completely Wrong" - Answer is factually incorrect or completely unrelated to the question
            - "Partially Missing" - Answer is partially correct but missing key information from reference
            - "Too Verbose" - Answer includes correct info but adds unnecessary or irrelevant details
            - "Accurate" - Answer is accurate and complete
            - "Comprehensive" - Answer covers reference content plus additional accurate context
            
            Provide a brief reason using one of these categories plus a short description.
            Example: "Comprehensive - covers expected answer plus relevant additional context"
            
            Return JSON with: 'question', 'llmAnswer', 'answer', 'score', 'reason'.

            QUESTION: {qaPairLLMAnswer.question}
            LLM ANSWER: {qaPairLLMAnswer.llmAnswer}
            REFERENCE ANSWER: {qaPairLLMAnswer.answer}
		"""
		
		completion = self.openai_client.chat.completions.parse(
			model=LLM_MODEL,
			messages=[{"role": "user", "content": prompt}],
			temperature=0.2,
			response_format=QAPairLLMEvaluation

		)
		
		message = completion.choices[0].message
		return message.parsed


