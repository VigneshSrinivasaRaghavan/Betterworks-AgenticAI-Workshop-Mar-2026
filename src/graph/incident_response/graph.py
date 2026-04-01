from langgraph.graph import StateGraph, END
from .state import IncidentState
from .supervisor import supervisor_router, supervisor_compile, route_next
from .agents import (
    log_analyzer_agent,
    root_cause_investigator_agent,
    solution_recommender_agent
)

def build_incident_response_graph():
    # Create Graph
    workflow = StateGraph(IncidentState)
    
    # Add Node
    workflow.add_node("router", supervisor_router)
    workflow.add_node("log_analyzer", log_analyzer_agent)
    workflow.add_node("root_cause_investigator", root_cause_investigator_agent)
    workflow.add_node("solution_recommender", solution_recommender_agent)
    workflow.add_node("compile_report", supervisor_compile)
    
    # Connect Nodes
    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_next,
        {
            "log_analyzer": "log_analyzer",
            "root_cause_investigator": "root_cause_investigator",
            "solution_recommender": "solution_recommender",
            "FINISH": "compile_report"
        }
    )
    
    workflow.add_edge("log_analyzer", "router")
    workflow.add_edge("root_cause_investigator", "router")
    workflow.add_edge("solution_recommender", "router")
    workflow.add_edge("compile_report", END)
    print("Graph Built Successfully")
    return workflow.compile()
    
    
