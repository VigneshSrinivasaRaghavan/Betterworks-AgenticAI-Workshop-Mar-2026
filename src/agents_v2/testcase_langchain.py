import sys
from pathlib import Path

# Langchain imports
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Core Utils
from src.core import get_langchain_llm, pick_requirement

# Prompt Template
from src.prompts.testcase_prompts import TESTCASE_SYSTEM_PROMPT

ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Build Langchain prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", TESTCASE_SYSTEM_PROMPT),
    ("user", "Requirement: \n\n{requirement}")
])

# Building the chain
llm = get_langchain_llm()
parser = JsonOutputParser()
chain = prompt_template | llm | parser


def main():
    
    # 1. Pick requirement file (from command line or auto-pick first)
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    req_file = pick_requirement(file_arg, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")
    
    print(f"📄 Processing: {req_file.name}")
    
    # 2. Run Chain
    testcases = chain.invoke({"requirement": requirement})  # Return the final testcase json from LLM
    
    # 3. Save Output
    import json
    import pandas as pd
    
    # Save the raw json
    raw_file = OUT_DIR / "raw_output_langchain.txt"
    raw_file.write_text(json.dumps(testcases, indent=2), encoding="utf-8")
    
    # Save CSV
    csv_file = OUT_DIR / "test_cases_langchain.csv"
    df = pd.DataFrame(testcases)
    df['steps'] = df['steps'].apply(lambda x: ' | '.join(x))
    df.to_csv(csv_file, index=False)
    
    print("Langchain Agent work is completed")

if __name__ == "__main__":
    main()
