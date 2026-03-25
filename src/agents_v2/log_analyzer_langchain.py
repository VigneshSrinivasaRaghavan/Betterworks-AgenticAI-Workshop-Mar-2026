# Python Core imports
import sys
import json
from pathlib import Path

# Langchain imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Core utils imports
from src.core import get_langchain_llm, pick_log_file

# Prompt Template imports
from src.prompts.log_analyzer_prompts import LOG_ANALYZER_SYSTEM_PROMPT

# Project paths
ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "data" / "logs"
OUT_DIR = ROOT / "outputs" / "log_analyzer"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", LOG_ANALYZER_SYSTEM_PROMPT),
    ("user", "Log file content: \n\n{log_content}")
])

# Build llm
llm = get_langchain_llm()

# Build Parser
parser = StrOutputParser()

# Build Chain
chain = prompt_template | llm | parser


def main():
    """Run the log analyzer agent."""
    
    # 1. Pick log file
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    log_file = pick_log_file(file_arg, LOG_DIR)
    log_content = log_file.read_text(encoding="utf-8")
    
    print(f"📄 Analyzing: {log_file.name}")
    print(f"📏 Log size: {len(log_content)} characters")
    
    # 2. Run chain
    response = chain.invoke({"log_content": log_content})
    
    # 3. Split response into 3 parts: text, JSON, executive
    text_report = response
    json_text = '{"error": "No JSON generated"}'
    exec_summary = "Executive summary not generated."
    
    # Extract JSON
    if "```json" in response:
        parts = response.split("```json")
        text_report = parts[0].strip()
        remainder = parts[1]
        
        if "```" in remainder:
            json_block = remainder.split("```")[0].strip()
            json_text = json_block
            
            # Extract executive summary
            after_json = remainder.split("```", 1)[1]
            if "---EXECUTIVE---" in after_json:
                exec_parts = after_json.split("---EXECUTIVE---")
                exec_summary = exec_parts[1].strip()
    
    # 5. Save text report
    report_file = OUT_DIR / f"{log_file.stem}_analysis.txt"
    report_file.write_text(text_report, encoding="utf-8")
    
    # 6. Save JSON
    try:
        json_data = json.loads(json_text)
        json_file = OUT_DIR / f"{log_file.stem}_analysis.json"
        json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        print(f"📊 JSON saved: {json_file.relative_to(ROOT)}")
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing failed: {e}")
    
    # 7. Save executive summary
    exec_file = OUT_DIR / f"{log_file.stem}_executive.txt"
    exec_file.write_text(exec_summary, encoding="utf-8")
    
    print(f"✅ Analysis complete")
    print(f"📝 Technical report: {report_file.relative_to(ROOT)}")
    print(f"👔 Executive summary: {exec_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
