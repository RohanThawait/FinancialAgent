import json
from tqdm import tqdm
# Import the initialized components from our app script
from app2 import create_agent, llm, db, memory

def run_evaluation():
    """
    Runs the evaluation pipeline against the dataset.
    """
    try:
        with open('evaluation_dataset.json', 'r') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print("Error: evaluation_dataset.json not found. Please create it first.")
        return

    # Create a fresh agent instance for the evaluation run
    agent = create_agent(llm, db, memory)
    
    correct_predictions = 0
    results_log = []

    print("🤖 Starting evaluation...")
    for item in tqdm(dataset, desc="Evaluating"):
        question = item["question"]
        expected_answer = item["answer"]
        
        try:
            result = agent.invoke({"input": question})
            agent_output = result["output"]
            # A simple way to check correctness is to see if the expected number/text is in the output
            is_correct = expected_answer.lower() in agent_output.lower()
        except Exception as e:
            agent_output = f"AGENT ERROR: {e}"
            is_correct = False

        if is_correct:
            correct_predictions += 1
        
        results_log.append({
            "question": question,
            "expected": expected_answer,
            "actual": agent_output,
            "correct": is_correct
        })

    # --- Print Detailed Report ---
    print("\n--- Evaluation Report ---")
    for res in results_log:
        status = "✅ CORRECT" if res["correct"] else "❌ INCORRECT"
        print(f"Q: {res['question']}")
        print(f"  - Expected to contain: '{res['expected']}'")
        print(f"  - Actual: '{res['actual']}'")
        print(f"  - Status: {status}\n")

    # --- Print Summary ---
    accuracy = (correct_predictions / len(dataset)) * 100
    print("--- Summary ---")
    print(f"Accuracy: {correct_predictions}/{len(dataset)} ({accuracy:.2f}%)")

if __name__ == "__main__":
    run_evaluation()