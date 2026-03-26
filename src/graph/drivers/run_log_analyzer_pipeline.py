"""
Driver for Log Analyzer Pipeline
"""
from src.graph.log_analyzer.graph import build_graph

def main():
    print("🚀 Starting Log Analyzer pipeline...")

    # Build graph
    app = build_graph()

    # Initialize empty state
    init_state = {
        "log_content": "",
        "analysis_text": "",
        "analysis_json": {},
        "executive_summary": "",
        "errors": []
    }

    # Run pipeline
    final_state = app.invoke(init_state)

    # Show results
    print(f"✅ Pipeline complete!")

    if final_state.get('errors'):
        print(f"Errors: {final_state['errors']}")
    else:
        print("Generated 3 reports: text, JSON, executive summary")

if __name__ == "__main__":
    main()
