from src.graph.test_case_generator.graph import build_graph

def main():
    # Build Graph
    app = build_graph()
    
    # Initialize empty State
    init_state = {
        "requirement": "",
        "test_cases": [],
        "errors": [],
        "validation_status": "pending",
        "retry_count": 0
    }
    
    # Run pipeline
    final_state = app.invoke(init_state)
    print(f"Pipeline complete!")
    print(f"Generated {len(final_state.get('test_cases', []))} test cases")
    
    if final_state.get("errors"):
        print("Errors:", final_state["errors"])
        
if __name__ == "__main__":
    main()