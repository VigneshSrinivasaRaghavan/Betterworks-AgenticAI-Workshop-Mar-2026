"""Utility functions for file and JSON handling."""

import json
from pathlib import Path
from typing import List, Dict


def pick_requirement(file_path: str = None, req_dir: str = "data/requirements") -> Path:
    """Select requirement file - either specific path or first .txt in directory."""

    # If specific file given, use it
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path

    # Otherwise, pick first .txt file
    txt_files = sorted(Path(req_dir).glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {req_dir}")

    return txt_files[0]

def parse_json_safely(text: str, raw_file: Path) -> List[Dict]:
    """Parse LLM text as JSON, handling markdown fences."""

    # Always save raw output for debugging
    raw_file.parent.mkdir(parents=True, exist_ok=True)
    raw_file.write_text(text, encoding="utf-8")

    # Try parsing directly first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except:
        pass

    # Cleanup: remove markdown code fences
    cleaned = text.strip()

    if cleaned.startswith("```"):
        # Remove backticks
        cleaned = cleaned.strip("`")
        # Remove first line if it's a language tag (e.g., "json")
        if "\n" in cleaned:
            lines = cleaned.split("\n", 1)
            if lines[0].strip() in ["json", "JSON", ""]:
                cleaned = lines[1]

    # Try parsing cleaned text
    data = json.loads(cleaned)

    if not isinstance(data, list):
        raise ValueError("Expected JSON array, got something else")

    return data

def pick_log_file(file_path: str = None, log_dir: str = "data/logs") -> Path:
    """Select log file - specific path or first .log file."""

    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")
        return path

    # Auto-pick first .log file
    log_files = sorted(Path(log_dir).glob("*.log"))
    if not log_files:
        raise FileNotFoundError(f"No .log files in {log_dir}")

    return log_files[0]
