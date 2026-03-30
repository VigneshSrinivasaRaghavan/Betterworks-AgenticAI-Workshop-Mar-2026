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
    """Read requirement file."""
    req_file = pick_requirement(None, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    return {"requirement": requirement}

def generate_tests(state: TestCaseState) -> TestCaseState:
    """Generate test cases with LLM."""
    requirement = state["requirement"]
    context = state.get("retrieved_context","")
    
    user_message = f"""" Based on the following company documentation
    
    {context}
    
    ---
    
    Now Generate testcases for the following requirement:
    
    {requirement}
    
"""

    try:
        # Call LLM
        response = chain.invoke({"requirement": user_message})

        # Parse JSON
        testcases = json.loads(response)

        return {"test_cases": testcases, "errors": []}

    except json.JSONDecodeError as e:
        return {"test_cases": [], "errors": [f"JSON parse error: {e}"]}
    except Exception as e:
        return {"test_cases": [], "errors": [f"LLM error: {e}"]}

def save_outputs(state: TestCaseState) -> TestCaseState:
    """Save test cases to files."""
    test_cases = state["test_cases"]

    if not test_cases:
        return {}

    # Save raw JSON
    raw_file = OUT_DIR / "raw_output.txt"
    raw_file.write_text(json.dumps(test_cases, indent=2), encoding="utf-8")

    # Save CSV
    df = pd.DataFrame(test_cases)
    if 'steps' in df.columns:
        df['steps'] = df['steps'].apply(lambda x: ' | '.join(x) if isinstance(x, list) else x)

    csv_file = OUT_DIR / "test_cases.csv"
    df.to_csv(csv_file, index=False)
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