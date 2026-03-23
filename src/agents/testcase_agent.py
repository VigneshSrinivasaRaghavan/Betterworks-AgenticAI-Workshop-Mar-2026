"""Test case generator agent."""

import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd
from src.core import chat, pick_requirement, parse_json_safely

# Project paths
ROOT = Path(__file__).resolve().parents[2]
REQ_DIR = ROOT / "data" / "requirements"
OUT_DIR = ROOT / "outputs" / "testcase_generated"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """You are a QA engineer. Generate test cases from requirements.

Return ONLY a JSON array with this structure:
[
  {
    "id": "TC-001",
    "title": "Short test title",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "expected": "Expected result",
    "priority": "High"
  }
]

Rules:
- Return 5 test cases
- Cover positive and negative scenarios
- Include edge cases
- Keep steps clear and actionable
- Priority: High, Medium, or Low
- Return ONLY JSON, no markdown fences"""


def save_as_csv(test_cases: List[Dict], csv_file: Path) -> None:
    """Convert test cases to CSV using pandas."""

    rows = []
    for i, case in enumerate(test_cases, 1):
        # Extract fields with defaults
        test_id = case.get("id", f"TC-{i:03d}")
        title = case.get("title", "")
        expected = case.get("expected", "")
        priority = case.get("priority", "Medium")

        # Handle steps (list or string)
        steps = case.get("steps", [])
        if isinstance(steps, list):
            steps_text = " | ".join(steps)
        else:
            steps_text = str(steps)

        rows.append({
            "TestID": test_id,
            "Title": title,
            "Steps": steps_text,
            "Expected": expected,
            "Priority": priority
        })

    # Create DataFrame and save
    df = pd.DataFrame(rows)
    df.to_csv(csv_file, index=False, encoding="utf-8")


def main():
    """Run the test case generator agent."""

    # 1. Pick requirement file (from command line or auto-pick first)
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    req_file = pick_requirement(file_arg, REQ_DIR)
    requirement = req_file.read_text(encoding="utf-8")

    print(f"📄 Processing: {req_file.name}")

    # 2. Build messages for LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Requirement:\n\n{requirement}"}
    ]

    # 3. Call LLM
    print("🤖 Calling LLM...")
    response = chat(messages)

    # 4. Parse JSON response
    raw_file = OUT_DIR / "raw_output.txt"
    test_cases = parse_json_safely(response, raw_file)

    print(f"✅ Generated {len(test_cases)} test cases")
    print(f"📝 Raw output saved: {raw_file.relative_to(ROOT)}")
    
    # 5. Save as CSV
    csv_file = OUT_DIR / "test_cases.csv"
    save_as_csv(test_cases, csv_file)


if __name__ == "__main__":
    main()
