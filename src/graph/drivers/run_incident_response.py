"""
Driver for Incident Response Multi-Agent System
"""
import sys
from pathlib import Path
from src.graph.incident_response.graph import build_incident_response_graph
from src.core import pick_log_file

# Paths
ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = ROOT / "data" / "logs"
OUT_DIR = ROOT / "outputs" / "incident_response"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("🚀 Starting Incident Response Multi-Agent System...")

    # Pick log file
    file_arg = sys.argv[1] if len(sys.argv) > 1 else None
    log_file = pick_log_file(file_arg, LOG_DIR)
    log_content = log_file.read_text(encoding="utf-8")

    print(f"Processing log: {log_file.name}")
    print(f"Log size: {len(log_content)} characters")

    # Build multi-agent graph
    app = build_incident_response_graph()

    # Initialize state
    init_state = {
        "log_content": log_content,
        "next_agent": "",
        "log_analysis": None,
        "root_cause": None,
        "solution": None,
        "incident_report": "",
        "steps_completed": [],
        "errors": []
    }

    # Run multi-agent workflow
    print("=" * 70)
    final_state = app.invoke(init_state)
    print("=" * 70)

    # Save incident report
    if final_state.get("errors"):
        print(f"⚠️ Workflow completed with errors: {final_state['errors']}")
    else:
        print("✅ Workflow completed successfully!")

    # Save report to file
    report_file = OUT_DIR / "incident_report.txt"
    report_file.write_text(final_state["incident_report"], encoding="utf-8")
    print(f"📄 Incident report saved: {report_file.relative_to(ROOT)}")

    # Show summary
    print(f"📊 Agents executed: {', '.join(final_state['steps_completed'])}")

    # Print report preview (first 500 chars)
    print("\\n" + "="*70)
    print("REPORT PREVIEW:")
    print("="*70)
    print(final_state["incident_report"][:500] + "...\\n")

if __name__ == "__main__":
    main()
