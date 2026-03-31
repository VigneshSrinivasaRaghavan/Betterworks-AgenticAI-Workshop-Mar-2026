"""
TestCase Generator - Node Functions
"""
import json
from pathlib import Path
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import TestCaseState
from src.core import get_langchain_llm, pick_requirement, search_vector_store
from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT
from src.core import PersistentMemory

persistent_memory = PersistentMemory(collection_name="testcase_memory")

# Setup
ROOT = Path(__file__).resolve().parents[3]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain components
llm = get_langchain_llm()
prompt_template = ChatPromptTemplate.from_messages([
    ("system", TESTCASE_SYSTEM_PROMPT),
    ("user", "Requirements:\n\n{requirement}")
])
parser = StrOutputParser()
chain = prompt_template | llm | parser

def read_requirement(state: TestCaseState) -> TestCaseState:
    """Read requirement file on first run. Skip if requirement already set by driver or follow-up."""
    if state.get("requirement"):
        if state.get("conversation_history"):
            # Actual follow-up — user typed an instruction in the CLI loop
            print(f"Follow-up instruction: {state['requirement'][:60]}...")
        else:
            # Requirement passed via CLI arg on first run
            print(f"Requirement loaded from file.")
        return {}
    req_file = pick_requirement(None, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    return {"requirement": requirement}

def generate_tests(state: TestCaseState) -> TestCaseState:
    """Generate test cases using RAG + STM + LTM context."""
    requirement = state["requirement"]
    retrieved_context = state.get("retrieved_context", "")
    past_patterns = state.get("past_patterns", "")
    conversation_history = state.get("conversation_history", [])
    existing_test_cases = state.get("test_cases", [])  # restored from checkpoint by MemorySaver

    # Build conversation context from STM (last 6 messages)
    conversation_text = ""
    if conversation_history:
        lines = [f"{msg['role']}: {msg['content']}" for msg in conversation_history[-6:]]
        conversation_text = "\n".join(lines)

    # Compose prompt — three context sources + requirement
    user_message = f"""COMPANY TESTING GUIDELINES:
{retrieved_context}
"""
    if past_patterns:
        user_message += f"""
PAST TEST CASE PATTERNS (from previous sessions):
{past_patterns}
"""

    if conversation_history and existing_test_cases:
        # Follow-up mode — LLM must ADD to existing test cases, not regenerate
        existing_json = json.dumps(existing_test_cases, indent=2)
        user_message += f"""
CONVERSATION HISTORY (current session):
{conversation_text}

EXISTING TEST CASES (already generated in this session):
{existing_json}

FOLLOW-UP INSTRUCTION: {requirement}
Add the requested test cases to the existing list above.
Return ALL test cases (existing + new ones) as a single JSON array.
Do NOT regenerate existing ones — only append new ones with the next available TC IDs.
"""
    else:
        # First run — generate fresh
        user_message += f"""
REQUIREMENT:
{requirement}
"""

    try:
        response = chain.invoke({"requirement": user_message})
        testcases = json.loads(response)

        # Update STM — append this turn to conversation history
        updated_history = list(conversation_history)
        updated_history.append({"role": "user", "content": requirement})
        tc_ids = ", ".join(tc.get("id", "") for tc in testcases)
        updated_history.append({
            "role": "agent",
            "content": f"Generated {len(testcases)} test case(s): {tc_ids}"
        })

        return {
            "test_cases": testcases,
            "errors": [],
            "conversation_history": updated_history
        }

    except json.JSONDecodeError as e:
        return {"test_cases": [], "errors": [f"JSON parse error: {e}"]}
    except Exception as e:
        return {"test_cases": [], "errors": [f"LLM error: {e}"]}

def save_outputs(state: TestCaseState) -> TestCaseState:
    """Save test cases to files. LTM save happens in driver after user confirms."""
    from datetime import datetime
    test_cases = state["test_cases"]

    if not test_cases:
        return {}

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw JSON — timestamped so sessions don't overwrite each other
    raw_file = OUT_DIR / f"raw_output_{timestamp}.txt"
    raw_file.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")

    # Save CSV — timestamped
    df = pd.DataFrame(test_cases)
    if "steps" in df.columns:
        df["steps"] = df["steps"].apply(
            lambda x: " | ".join(x) if isinstance(x, list) else x
        )
    csv_file = OUT_DIR / f"test_cases_{timestamp}.csv"
    df.to_csv(csv_file, index=False)

    print(f"Saved {len(test_cases)} test cases to {OUT_DIR}")
    return {}


def validate_tests(state: TestCaseState) -> TestCaseState:
    test_cases = state.get("test_cases",[])
    
    if len(test_cases) < 3:
        return {"validation_status": "fail"}
    
    required_fields = ["id", "title", "steps", "expected", "priority"]
    for tc in test_cases:
        missing = [f for f in required_fields if f not in tc or not tc[f]]
        if missing:
            return {"validation_status": "fail"}
        
        # Check steps is a list with at least 2 steps
        if not isinstance(tc["steps"], list) or len(tc["steps"]) < 2:
            return {"validation_status": "fail"}
    
    return {"validation_status": "pass"}

def retry_generate(state: TestCaseState) -> TestCaseState:
    """Retry test case generation."""
    retry_count = state.get("retry_count", 0) + 1

    # Generate again (same logic as generate_tests)
    try:
        response = chain.invoke({"requirement": state["requirement"]})
        testcases = json.loads(response)

        return {
            "test_cases": testcases,
            "errors": [],
            "retry_count": retry_count,
            "validation_status": "pending"
        }

    except json.JSONDecodeError as e:
        return {
            "test_cases": [],
            "errors": [f"JSON parse error: {e}"],
            "retry_count": retry_count,
            "validation_status": "fail"
        }
    except Exception as e:
        return {
            "test_cases": [],
            "errors": [f"LLM error: {e}"],
            "retry_count": retry_count,
            "validation_status": "fail"
        }

def route_after_validation(state: TestCaseState) -> str:
    """Decide next node based on validation result."""

    validation_status = state.get("validation_status", "pending")
    retry_count = state.get("retry_count", 0)

    # If passed validation → save
    if validation_status == "pass":
        print("Validation passed! Saving test cases...")
        return "save"

    # If failed but can retry → retry
    if validation_status == "fail" and retry_count < 3:
        print("Validation failed. Retrying...")
        return "retry"

    # If max retries reached → save anyway
    return "save"

def retrieve_context(state: TestCaseState) -> TestCaseState:
    requirement = state["requirement"]
    print(f"Retrieving context for requirement")
    results = search_vector_store(query=f"test case guidelines for {requirement}")
    return {"retrieved_context": results}

def load_memories(state: TestCaseState) -> TestCaseState:
    """Load STM (from state) and LTM (from ChromaDB) before generation."""
    requirement = state.get("requirement", "")
    conversation_history = state.get("conversation_history", [])

    # STM is already in state — restored automatically by MemorySaver
    print(f"Loaded conversation history: {len(conversation_history)} message(s)")

    # LTM — semantic search for past test patterns
    past_patterns = persistent_memory.get_context(
        query=f"test case patterns for {requirement[:100]}",
        top_k=2
    )

    return {"past_patterns": past_patterns}