"""
Log Analyzer - Graph Assembly
"""
from langgraph.graph import StateGraph, END
from .state import LogAnalyzerState
from .nodes import read_log, analyze_log, save_outputs

def build_graph():
    # Create graph
    workflow = StateGraph(LogAnalyzerState)

    # Add nodes
    workflow.add_node("read", read_log)
    workflow.add_node("analyze", analyze_log)
    workflow.add_node("save", save_outputs)

    # Connect nodes
    workflow.set_entry_point("read")
    workflow.add_edge("read", "analyze")
    workflow.add_edge("analyze", "save")
    workflow.add_edge("save", END)

    # Compile
    return workflow.compile()
