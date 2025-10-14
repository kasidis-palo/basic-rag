# Simple Evaluation - LLM-as-a-Judge

A RAG evaluation pipeline using LLM-as-a-judge methodology to assess answer quality.

## Core Functions

### 1. QA Pair Generation (`prepare_qa_pairs.py`)
- Extracts content from PDF documents
- Generates question-answer pairs using LLM
- Stores pairs in JSONL format

### 2. RAG Answer Generation (`prepare_llm_answers_from_qa_pairs.py`)
- Uses RAG system to answer generated questions
- Compares RAG answers with ground truth
- Outputs LLM responses for evaluation

### 3. LLM-as-Judge Evaluation (`evaluate_llm_as_a_judge.py`)
- Evaluates RAG answers using LLM judge
- Scores answers on 0-5 scale with reasoning
- Produces evaluation results with detailed feedback

### 4. Report Generation (`generate_evaluation_report.py`)
- Creates comprehensive evaluation reports
- Calculates metrics and statistics
- Generates markdown reports with insights

### 5. Main Pipeline (`main_evaluation.py`)
- Interactive terminal interface
- Runs complete evaluation pipeline
- Supports step-by-step or full automation

## Folder Structure

```
evaluation/
├── data/
│   ├── qa_pairs/          # Generated question-answer pairs
│   ├── llm_answers/       # RAG system responses
│   ├── evaluation/        # LLM judge evaluation results
│   └── report/           # Generated evaluation reports
├── models/               # Pydantic data models
├── utils/               # Utility functions (LLM, files, documents)
└── *.py                # Main pipeline scripts
```

## Quick Start

1. Run the main evaluation interface:
   ```bash
   python main_evaluation.py
   ```

2. Or run individual steps:
   - Generate QA pairs: `python prepare_qa_pairs.py`
   - Generate RAG answers: `python prepare_llm_answers_from_qa_pairs.py`
   - Evaluate with LLM judge: `python evaluate_llm_as_a_judge.py`
   - Generate report: `python generate_evaluation_report.py`

## Requirements

- OpenAI/Ollama API access
- Qdrant vector database running on localhost:6333
- PDF source document: `on-the-rheology-of-cats.pdf`

## Qdrant Dashboard

- http://localhost:6333/dashboard#/welcome