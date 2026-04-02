from typing import TypedDict, List, Dict

class TestCaseState(TypedDict):
    requirement: str
    conversation_history: List[Dict]
    past_patterns: str
    retrieved_context: str
    test_cases: List[Dict]
    errors: List[str]
    validation_status: str
    retry_count: int
    target_url: str
    execution_results: List[Dict]