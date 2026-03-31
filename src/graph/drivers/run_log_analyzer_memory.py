"""
Log Analyzer with Memory — Interactive Driver

STM: MemorySaver keeps conversation_history alive across invocations in this session
LTM: PersistentMemory (ChromaDB) stores approved incident analyses for future sessions

Run: python -m src.graph.drivers.run_log_analyzer_memory
Run with specific file: python -m src.graph.drivers.run_log_analyzer_memory data/logs/application_error.log
"""
import sys
import uuid
from pathlib import Path
from src.graph.log_analyzer_memory.graph import build_graph
from src.graph.log_analyzer_memory.nodes import persistent_memory

def display_analysis(state: dict):
    print("\n" + "=" * 60)
    print("Log Analysis Result:")
    print("=" * 60)

    exec_summary = state.get("executive_summary", "")
    if exec_summary:
        print("\nExecutive Summary:")
        print(exec_summary)

    analysis_json = state.get("analysis_json", {})
    if analysis_json and isinstance(analysis_json, dict):
        print(f"\nSeverity   : {analysis_json.get('severity', 'unknown').upper()}")
        print(f"Error Count: {analysis_json.get('error_count', 0)}")

        root_causes = analysis_json.get("root_causes", [])
        if root_causes:
            print("\nRoot Causes:")
            for rc in root_causes:
                print(f"  • {rc}")

        recommendations = analysis_json.get("recommendations", [])
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"  • {rec}")

    print("=" * 60)


def main():
    app = build_graph()

    # Unique thread_id for this session — STM is scoped to this ID
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 60)
    print("Log Analyzer with Memory")
    print("=" * 60)
    print(f"Session ID: {thread_id[:8]}...")

    # Read log from CLI arg if provided, otherwise let read_log node auto-pick
    log_content = ""
    if len(sys.argv) > 1:
        log_path = Path(sys.argv[1])
        if not log_path.exists():
            print(f"File not found: {log_path}")
            return
        log_content = log_path.read_text(encoding="utf-8")
        print(f"Log file: {log_path.name}")

    # --- First run: analyze the log ---
    init_state = {
        "log_content": log_content,
        "user_instruction": "",
        "conversation_history": [],
        "past_incidents": "",
        "retrieved_context": "",
        "analysis_text": "",
        "analysis_json": {},
        "executive_summary": "",
        "errors": []
    }

    result = app.invoke(init_state, config=config)

    if result.get("errors"):
        print("Errors:", result["errors"])
        return

    display_analysis(result)

    # --- Interactive follow-up loop ---
    while True:
        print("\nOptions:")
        print("  • Type a follow-up instruction (e.g. 'focus more on the timeout errors')")
        print("  • Type 'save' to approve and save this incident to memory")
        print("  • Type 'quit' to exit without saving")

        user_input = input("\nYour input: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("Exiting without saving to memory.")
            break

        if user_input.lower() == "save":
            # Save approved incident analysis to LTM
            analysis_json = result.get("analysis_json", {})
            log_preview = result.get("log_content", "")[:100] if result.get("log_content") else ""

            root_causes = "; ".join(analysis_json.get("root_causes", []))
            affected = "; ".join(analysis_json.get("affected_systems", []))
            recommendations = "; ".join(analysis_json.get("recommendations", []))

            ltm_text = (
                f"Incident summary: {analysis_json.get('summary', 'N/A')}\n"
                f"Severity: {analysis_json.get('severity', 'unknown')}\n"
                f"Error count: {analysis_json.get('error_count', 0)}\n"
                f"Root causes: {root_causes}\n"
                f"Affected systems: {affected}\n"
                f"Recommendations: {recommendations}"
            )
            persistent_memory.store_interaction(
                text=ltm_text,
                metadata={
                    "type": "log_analysis",
                    "severity": analysis_json.get("severity", "unknown"),
                    "error_count": analysis_json.get("error_count", 0),
                    "log_preview": log_preview
                }
            )
            print("\nIncident saved to long-term memory! Agent will recall this next time a similar log appears.")
            break

        # Follow-up invocation — same thread_id so MemorySaver restores STM
        follow_up_state = {
            "user_instruction": user_input,
            "errors": []
        }
        result = app.invoke(follow_up_state, config=config)

        if result.get("errors"):
            print("Errors:", result["errors"])
        else:
            display_analysis(result)


if __name__ == "__main__":
    main()
