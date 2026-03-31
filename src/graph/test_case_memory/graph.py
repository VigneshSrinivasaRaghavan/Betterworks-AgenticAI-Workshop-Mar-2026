from langgraph.graph import StateGraph, END
from .state import TestCaseState
from .nodes import read_requirement, retrieve_context, generate_tests, save_outputs, validate_tests, retry_generate, route_after_validation, load_memories
from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    # Create Graph
    workflow = StateGraph(TestCaseState)
    
    # Add Nodes
    workflow.add_node("read_requirement",read_requirement)
    workflow.add_node("load_memories",load_memories)
    workflow.add_node("retrieve_context",retrieve_context)
    workflow.add_node("generate_tests",generate_tests)
    workflow.add_node("save_outputs",save_outputs)
    workflow.add_node("validate_tests",validate_tests)
    workflow.add_node("retry_generate",retry_generate)
    workflow.add_node("route_after_validation",route_after_validation)
    
    # Linear Edge Connections
    workflow.set_entry_point("read_requirement")
    workflow.add_edge("read_requirement","load_memories")
    workflow.add_edge("load_memories","retrieve_context")
    workflow.add_edge("retrieve_context","generate_tests")
    workflow.add_edge("generate_tests","validate_tests")
    
    # Conditional Edge Connections
    workflow.add_conditional_edges(
        "validate_tests",  # From this node
        route_after_validation,
        {
            "save": "save_outputs",
            "retry": "retry_generate"
        }# Use this function to decide
    )
    
    # Retry Loop back to validate_tests
    workflow.add_edge("retry_generate","validate_tests")
    
    
    # Linear Edge Connections
    workflow.add_edge("save_outputs", END)
    
    # Memory Saver - Enabled Short Term Memory
    checkpointer = MemorySaver()
    
    # Compile
    return workflow.compile(checkpointer=checkpointer)