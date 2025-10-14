from pydantic import BaseModel
from typing import List

class QAPair(BaseModel):
    question: str
    answer: str

class QAPairList(BaseModel):
    qa_pairs: List[QAPair]

class QAPairLLMAnswer(QAPair):
    llmAnswer: str


class QAPairLLMEvaluation(QAPairLLMAnswer):
    score: int  # Score from 0 to 5
    reason: str 