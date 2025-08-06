"""
Evaluation Script for the AI Finance Agent.

This script tests the accuracy of the LangChain agent against a predefined
set of questions and expected answers from an evaluation dataset.

It performs the following steps:
1. Loads the evaluation dataset from a JSON file.
2. Initializes the agent for a default test user ('jsmith').
3. Iterates through each question, invoking the agent.
4. Compares the agent's output to the expected answer.
5. Prints a detailed report and a final accuracy score.

To run, execute `python run_evaluation.py` from the project's root directory.
"""

# --- Imports ---
import json
from tqdm import tqdm

# Import the agent setup function from the core application logic
from app_logic import setup_agent

# --- Configuration Constants ---
DATASET_FILE = "evaluation_dataset.json"
TEST_USERNAME = "jsmith"
TEST_NAME = "John Smith"

# --- Helper Functions ---

def load_dataset(file_path: str) -> list | None:
    """
    Loads the evaluation dataset from a JSON file.

    Args:
        file_path: The path to the JSON dataset file.

    Returns:
        A list of dictionaries representing the dataset, or None if an error occurs.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f" Error: Evaluation dataset not found at '{file_path}'.")
        return None
    except json.JSONDecodeError:
        print(f" Error: Could not decode JSON from '{file_path}'. Please check its format.")
        return None

def print_report(results: list):
    """
    Formats and prints the final evaluation report and accuracy summary.

    Args:
        results: A list of dictionaries, where each dictionary contains the
                 evaluation result for a single question.
    """
    print("\n--- Evaluation Report ---")
    correct_predictions = 0
    for res in results:
        status = "CORRECT" if res["correct"] else "INCORRECT"
        print(f"\nQ: {res['question']}")
        print(f"  - Expected to contain: '{res['expected']}'")
        print(f"  - Actual: '{res['actual']}'")
        print(f"  - Status: {status}")
        if res["correct"]:
            correct_predictions += 1
    
    total_questions = len(results)
    accuracy = (correct_predictions / total_questions) * 100 if total_questions > 0 else 0
    
    print("\n--- Summary ---")
    print(f"Accuracy: {correct_predictions}/{total_questions} ({accuracy:.2f}%)")

# --- Main Evaluation Logic ---

def run_evaluation():
    """
    Orchestrates the entire evaluation pipeline.
    """
    dataset = load_dataset(DATASET_FILE)
    if not dataset:
        return

    print(f"Initializing agent for test user '{TEST_USERNAME}'...")
    agent = setup_agent(username=TEST_USERNAME, name=TEST_NAME)
    
    results_log = []
    print(f"\nStarting evaluation on {len(dataset)} questions...")
    
    for item in tqdm(dataset, desc="Evaluating Agent"):
        question = item["question"]
        expected_answer = item["answer"]
        
        try:
            result = agent.invoke({"input": question})
            agent_output = result.get("output", "No output found.")
            # Check if the expected answer substring is in the agent's output
            is_correct = expected_answer.lower() in agent_output.lower()
        except Exception as e:
            agent_output = f"AGENT ERROR: {e}"
            is_correct = False
        
        results_log.append({
            "question": question,
            "expected": expected_answer,
            "actual": agent_output,
            "correct": is_correct
        })

    print_report(results_log)

def main():
    """Main entry point for the script."""
    run_evaluation()

if __name__ == "__main__":
    main()