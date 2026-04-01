"""
Root Cause Investigator Agent - Finds root cause
"""
from src.core import get_langchain_llm
from src.prompts import ROOT_CAUSE_PROMPT
from langchain_core.output_parsers import StrOutputParser

# Initialize LLM and chain
llm = get_langchain_llm()
parser = StrOutputParser()
chain = llm | parser

def root_cause_investigator_agent(state):
    """Investigate and determine root cause."""
    print("Root Cause Investigator running...")

    log_analysis = state.get("log_analysis", "")
    log_content = state["log_content"]

    try:
        # Call LLM to find root cause
        prompt = ROOT_CAUSE_PROMPT.format(
            log_analysis=log_analysis,
            log_content=log_content
        )
        root_cause = chain.invoke(prompt)

        print(f"✅ Root cause identified ({len(root_cause)} chars)")

        return {
            "root_cause": root_cause,
            "steps_completed": state["steps_completed"] + ["root_cause_investigator"]
        }

    except Exception as e:
        print(f"❌ Root Cause Investigator failed: {e}")
        return {
            "root_cause": f"Error: {e}",
            "steps_completed": state["steps_completed"] + ["root_cause_investigator"],
            "errors": state["errors"] + [f"Root Cause Investigator: {e}"]
        }
