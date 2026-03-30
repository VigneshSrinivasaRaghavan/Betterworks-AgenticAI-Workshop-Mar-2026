from typing import TypedDict, List, Dict

class TestCaseState(TypedDict):
    requirement: str
    retrieved_context: str
    test_cases: List[Dict]
    errors: List[str]
    validation_status: str
    retry_count: int