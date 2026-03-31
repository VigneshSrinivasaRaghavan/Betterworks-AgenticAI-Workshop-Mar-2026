"""
TestCase Generator with Memory — Interactive Driver

STM: MemorySaver keeps conversation_history alive across invocations in this session
LTM: PersistentMemory (ChromaDB) stores approved outputs for future sessions

Run: python -m src.graph.drivers.run_test_case_memory
Run with specific file: python -m src.graph.drivers.run_test_case_memory data/requirements/payment_checkout.txt
"""
import sys
import uuid
from pathlib import Path
from src.graph.test_case_memory.graph import build_graph
from src.graph.test_case_memory.nodes import persistent_memory


def display_test_cases(test_cases: list):
    print("\n" + "=" * 60)
    print(f"Generated {len(test_cases)} Test Case(s):")
    print("=" * 60)
    for tc in test_cases:
        print(f"\n  [{tc.get('priority', '?')}] {tc.get('id', '?')} — {tc.get('title', '?')}")
        for step in tc.get("steps", []):
            print(f"    • {step}")
        print(f"    Expected: {tc.get('expected', '?')}")
    print("=" * 60)


def main():
    app = build_graph()

    # Unique thread_id for this session — STM is scoped to this ID
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 60)
    print("TestCase Generator with Memory")
    print("=" * 60)
    print(f"Session ID: {thread_id[:8]}...")

    # Read requirement from CLI arg if provided, otherwise let read_requirement node pick
    requirement = ""
    if len(sys.argv) > 1:
        req_path = Path(sys.argv[1])
        if not req_path.exists():
            print(f"File not found: {req_path}")
            return
        requirement = req_path.read_text(encoding="utf-8")
        print(f"Requirement file: {req_path.name}")

    # --- First run: read requirement from file ---
    init_state = {
        "requirement": requirement,
        "conversation_history": [],
        "past_patterns": "",
        "retrieved_context": "",
        "test_cases": [],
        "errors": [],
        "validation_status": "pending",
        "retry_count": 0
    }

    result = app.invoke(init_state, config=config)
    test_cases = result.get("test_cases", [])

    if result.get("errors"):
        print("Errors:", result["errors"])

    if test_cases:
        display_test_cases(test_cases)
    else:
        print("No test cases generated.")
        return

    # --- Interactive follow-up loop ---
    while True:
        print("\nOptions:")
        print("  • Type a follow-up instruction (e.g. 'add 2 more for logout flow')")
        print("  • Type 'save' to approve and save to memory")
        print("  • Type 'quit' to exit without saving")

        user_input = input("\nYour input: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Exiting without saving to memory.")
            break

        if user_input.lower() == "save":
            # Save approved test cases to LTM
            requirement = result.get("requirement", "")
            tc_summary = "; ".join(
                f"{tc.get('id','')} - {tc.get('title','')}" for tc in test_cases
            )
            ltm_text = (
                f"Requirement: {requirement[:200]}\n"
                f"Generated {len(test_cases)} test case(s): {tc_summary}"
            )
            persistent_memory.store_interaction(
                text=ltm_text,
                metadata={
                    "type": "test_case",
                    "count": len(test_cases),
                    "requirement_preview": requirement[:100]
                }
            )
            print("\nSaved to long-term memory! Agent will recall these patterns next session.")
            break

        # Follow-up invocation — same thread_id so MemorySaver restores STM
        follow_up_state = {
            "requirement": user_input,
            "validation_status": "pending",
            "retry_count": 0
        }
        result = app.invoke(follow_up_state, config=config)
        test_cases = result.get("test_cases", [])

        if result.get("errors"):
            print("Errors:", result["errors"])

        if test_cases:
            display_test_cases(test_cases)
        else:
            print("No test cases generated on follow-up.")


if __name__ == "__main__":
    main()