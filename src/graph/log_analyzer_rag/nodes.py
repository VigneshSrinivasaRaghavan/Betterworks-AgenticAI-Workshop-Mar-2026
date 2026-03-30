"""
Log Analyzer - Node Functions
"""
import json
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import LogAnalyzerState
from src.core import get_langchain_llm, pick_log_file
from src.prompts.log_analyzer_prompts import LOG_ANALYZER_SYSTEM_PROMPT
from src.core import search_vector_store

# Setup
ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "data" / "logs"
OUT_DIR = ROOT / "outputs" / "log_analyzer"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain components
llm = get_langchain_llm()
prompt_template = ChatPromptTemplate.from_messages([
    ("system", LOG_ANALYZER_SYSTEM_PROMPT),
    ("user", "Analyze this log:\n\n{log_content}")
])
parser = StrOutputParser()
chain = prompt_template | llm | parser


def read_log(state: LogAnalyzerState) -> LogAnalyzerState:
    """Read log file."""
    log_file = pick_log_file(None, LOG_DIR)
    log_content = log_file.read_text(encoding="utf-8")
    return {"log_content": log_content}


def analyze_log(state: LogAnalyzerState) -> LogAnalyzerState:
    """Analyze log with LLM (returns 3 parts)."""
    log_content = state["log_content"]
    context = state.get("retrieved_context", "")
    
    user_message = f"""Based on the following troubleshooting guides:

{context}

---

Now analyze this log:

{log_content}"""

    try:
        # Call LLM
        response = chain.invoke({"log_content": user_message})

        # Parse 3-part response
        text_report, json_report, exec_summary = _split_response(response)

        return {
            "analysis_text": text_report,
            "analysis_json": json_report,
            "executive_summary": exec_summary,
            "errors": []
        }

    except Exception as e:
        return {
            "analysis_text": "",
            "analysis_json": {},
            "executive_summary": "",
            "errors": [f"LLM error: {e}"]
        }


def save_outputs(state: LogAnalyzerState) -> LogAnalyzerState:
    """Save analysis to 3 files."""

    if state.get("errors"):
        return {}

    # Save text analysis
    text_file = OUT_DIR / "analysis_report.txt"
    text_file.write_text(state["analysis_text"], encoding="utf-8")

    # Save JSON report
    json_file = OUT_DIR / "analysis_report.json"
    json_file.write_text(
        json.dumps(state["analysis_json"], indent=2),
        encoding="utf-8"
    )

    # Save executive summary
    exec_file = OUT_DIR / "executive_summary.txt"
    exec_file.write_text(state["executive_summary"], encoding="utf-8")
    return {}


def _split_response(response: str) -> tuple:
    """Split LLM response into 3 parts."""
    text_report = response
    json_report = {}
    exec_summary = "Executive summary not generated."

    # Split by ```json markdown fence
    if "```json" in response:
        parts = response.split("```json")
        text_report = parts[0].strip()
        remainder = parts[1]

        # Extract JSON
        if "```" in remainder:
            json_block = remainder.split("```")[0].strip()
            try:
                json_report = json.loads(json_block)
            except json.JSONDecodeError:
                json_report = {"error": "Failed to parse JSON"}

            # Extract executive summary
            after_json = remainder.split("```", 1)[1]
            if "---EXECUTIVE---" in after_json:
                exec_parts = after_json.split("---EXECUTIVE---")
                exec_summary = exec_parts[1].strip()

    return text_report, json_report, exec_summary

def retrieve_context(state: LogAnalyzerState) -> LogAnalyzerState:
    log_content = state["log_content"]
    print(f"Retrieving context for Log Content")
    results = search_vector_store(query=f"troubleshooting guide for {log_content}")
    return {"retrieved_context": results}