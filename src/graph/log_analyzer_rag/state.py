from typing import TypedDict, Dict, List

class LogAnalyzerState(TypedDict):
    log_content: str
    retrieved_context: str
    analysis_text: str
    analysis_json: Dict
    executive_summary: str
    errors: List[str]