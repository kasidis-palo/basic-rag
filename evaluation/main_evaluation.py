#!/usr/bin/env python3
"""
Main evaluation script with terminal interface for RAG evaluation pipeline.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all the main functions from root level files
from evaluation.prepare_qa_pairs import prepare_qa_pairs
from evaluation.prepare_llm_answers_from_qa_pairs import prepare_llm_answers_from_qa_pairs
from evaluation.evaluate_llm_as_a_judge import evaluate_llm_as_a_judge
from evaluation.generate_evaluation_report import generate_evaluation_report


def display_menu():
    """Display the main menu options."""
    print("\n" + "="*60)
    print("        RAG EVALUATION PIPELINE")
    print("="*60)
    print("1. Prepare QA")
    print("   Generate question-answer pairs from PDF documents")
    print()
    print("2. Prepare LLM Answer QA")
    print("   Generate LLM answers for the prepared QA pairs using RAG")
    print()
    print("3. Evaluate")
    print("   Evaluate LLM answers using LLM-as-a-judge approach")
    print()
    print("4. Report")
    print("   Generate comprehensive evaluation report")
    print()
    print("5. Run Full Pipeline")
    print("   Execute all steps in sequence (1 → 2 → 3 → 4)")
    print()
    print("0. Exit")
    print("="*60)


def get_user_choice():
    """Get and validate user choice."""
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            if choice in ['0', '1', '2', '3', '4', '5']:
                return choice
            else:
                print("Invalid choice. Please enter a number between 0 and 5.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
        except EOFError:
            print("\n\nExiting...")
            sys.exit(0)


def execute_step(step_num, step_name, step_function):
    """Execute a single step with error handling and progress indication."""
    print(f"\n{'='*20} STEP {step_num}: {step_name.upper()} {'='*20}")
    try:
        step_function()
        print(f"✅ Step {step_num} ({step_name}) completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error in Step {step_num} ({step_name}): {str(e)}")
        print("Please check the error above and try again.")
        return False


def run_full_pipeline():
    """Run the complete evaluation pipeline."""
    print("\n🚀 Starting Full RAG Evaluation Pipeline...")
    
    steps = [
        (1, "Prepare QA", prepare_qa_pairs),
        (2, "Prepare LLM Answer QA", prepare_llm_answers_from_qa_pairs),
        (3, "Evaluate", evaluate_llm_as_a_judge),
        (4, "Report", generate_evaluation_report)
    ]
    
    for step_num, step_name, step_function in steps:
        success = execute_step(step_num, step_name, step_function)
        if not success:
            print(f"\n❌ Full pipeline stopped at Step {step_num}")
            return False
    
    print("\n🎉 Full RAG Evaluation Pipeline completed successfully!")
    return True


def main():
    """Main function to run the evaluation interface."""
    print("Welcome to the RAG Evaluation System!")
    
    while True:
        display_menu()
        choice = get_user_choice()
        
        if choice == '0':
            print("\n👋 Thank you for using the RAG Evaluation System!")
            break
            
        elif choice == '1':
            execute_step(1, "Prepare QA", prepare_qa_pairs)
            
        elif choice == '2':
            execute_step(2, "Prepare LLM Answer QA", prepare_llm_answers_from_qa_pairs)
            
        elif choice == '3':
            execute_step(3, "Evaluate", evaluate_llm_as_a_judge)
            
        elif choice == '4':
            execute_step(4, "Report", generate_evaluation_report)
            
        elif choice == '5':
            run_full_pipeline()
        
        # Ask if user wants to continue
        if choice != '0':
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using the RAG Evaluation System!")
        sys.exit(0)
