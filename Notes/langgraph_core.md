- LangGraph Core Concepts
    
    ## What We'll Cover
    
    Learn the 3 building blocks of LangGraph: State, Nodes, and Edges with simple examples
    
    ---
    
    ## The 3 Building Blocks
    
    LangGraph has only **3 core concepts**:
    
    1. **State** - Data shared between steps
    2. **Nodes** - Functions that do work
    3. **Edges** - Connections between nodes
    
    That's it! Let's learn each one.
    
    ---
    
    ## Concept 1: State (Shared Data)
    
    ### What is State?
    
    State is a **dictionary** that flows through your graph. All nodes can read and update it.
    
    ### Simple Example:
    
    ```python
    from typing import TypedDict
    
    class AgentState(TypedDict):
        count: int
        message: str
    
    ```
    
    **That's it!** A state is just a TypedDict defining what data you'll track.
    
    ### Why TypedDict?
    
    ```python
    # Regular dict - no type hints
    state = {"count": 5, "message": "hello"}
    
    # TypedDict - Python knows the types
    class AgentState(TypedDict):
        count: int
        message: str
    
    ```
    
    **Benefit:** Python and your IDE can help catch bugs!
    
    ---
    
    ## Concept 2: Nodes (Functions)
    
    ### What is a Node?
    
    A node is a **function** that:
    
    - Takes state as input
    - Does some work
    - Returns updated state
    
    ### Simple Example:
    
    ```python
    def increment(state: AgentState) -> AgentState:
        return {"count": state["count"] + 1}
    
    ```
    
    **That's it!** Read from state, do work, return update.
    
    ### Node Pattern:
    
    ```python
    def node_name(state: StateType) -> StateType:
        # 1. Read from state
        value = state["key"]
    
        # 2. Do work
        new_value = value + 1
    
        # 3. Return update
        return {"key": new_value}
    
    ```
    
    **Remember:** Return only what changed (LangGraph merges it automatically)!
    
    ---
    
    ## Concept 3: Edges (Connections)
    
    ### What is an Edge?
    
    An edge is a **connection** between nodes. It says "after Node A, go to Node B".
    
    ### Two Types:
    
    **1. Normal Edge (always goes there):**
    
    ```python
    graph.add_edge("node_a", "node_b")
    # Always: node_a → node_b
    
    ```
    
    **2. Conditional Edge (decides where to go):**
    
    ```python
    graph.add_conditional_edges(
        "node_a",
        decide_function,
        {"path1": "node_b", "path2": "node_c"}
    )
    # Dynamic: node_a → ? (depends on state)
    
    ```
    
    We'll learn conditional edges later. For now, focus on normal edges.
    
    ---
    
    ## Putting It Together: First Graph
    
    Let's build a simple graph that counts!
    
    ### Step 1: Define State
    
    ```python
    from typing import TypedDict
    
    class CounterState(TypedDict):
        count: int
    
    ```
    
    ### Step 2: Define Nodes
    
    ```python
    def add_one(state: CounterState) -> CounterState:
        return {"count": state["count"] + 1}
    
    def add_two(state: CounterState) -> CounterState:
        return {"count": state["count"] + 2}
    
    ```
    
    ### Step 3: Build Graph
    
    ```python
    from langgraph.graph import StateGraph, END
    
    graph = StateGraph(CounterState)
    graph.add_node("add_one", add_one)
    graph.add_node("add_two", add_two)
    
    ```
    
    ### Step 4: Connect Nodes
    
    ```python
    graph.set_entry_point("add_one")
    graph.add_edge("add_one", "add_two")
    graph.add_edge("add_two", END)
    
    ```
    
    **Flow:**
    
    ```
    START → add_one → add_two → END
    
    ```
    
    ### Step 5: Compile and Run
    
    ```python
    app = graph.compile()
    result = app.invoke({"count": 0})
    print(result)
    # Output: {"count": 3}  (0 + 1 + 2)
    
    ```
    
    **Done!** That's a complete LangGraph workflow.
    
    ---
    
    ## Complete Working Example
    
    **Create:** `test_langgraph_concepts.py` (in project root)
    
    ```python
    from typing import TypedDict
    from langgraph.graph import StateGraph, END
    
    # 1. Define state
    class CounterState(TypedDict):
        count: int
    
    # 2. Define nodes
    def add_one(state: CounterState) -> CounterState:
        print(f"  add_one: {state['count']} → {state['count'] + 1}")
        return {"count": state["count"] + 1}
    
    def add_two(state: CounterState) -> CounterState:
        print(f"  add_two: {state['count']} → {state['count'] + 2}")
        return {"count": state["count"] + 2}
    
    # 3. Build graph
    graph = StateGraph(CounterState)
    graph.add_node("add_one", add_one)
    graph.add_node("add_two", add_two)
    
    # 4. Connect nodes
    graph.set_entry_point("add_one")
    graph.add_edge("add_one", "add_two")
    graph.add_edge("add_two", END)
    
    # 5. Compile and run
    app = graph.compile()
    
    print("Running graph:")
    result = app.invoke({"count": 0})
    print(f"\nFinal result: {result}")
    
    ```
    
    **Run:**
    
    ```bash
    python test_langgraph_concepts.py
    
    ```
    
    **Output:**
    
    ```
    Running graph:
      add_one: 0 → 1
      add_two: 1 → 3
    
    Final result: {'count': 3}
    
    ```
    
    **Clean up:**
    
    ```bash
    rm test_langgraph_concepts.py
    
    ```
    
    ---
    
    ## Understanding State Updates
    
    ### Important: Partial Updates!
    
    Nodes return **only what changed**, not the entire state.
    
    ```python
    # State has multiple fields
    class State(TypedDict):
        count: int
        message: str
        done: bool
    
    # Node updates only count
    def increment(state: State) -> State:
        return {"count": state["count"] + 1}
        # message and done stay unchanged!
    
    ```
    
    **LangGraph automatically merges** the update with existing state.
    
    ### Example:
    
    ```python
    # Initial state
    state = {"count": 0, "message": "hello", "done": False}
    
    # Node returns
    {"count": 1}
    
    # LangGraph merges to
    {"count": 1, "message": "hello", "done": False}
    
    ```
    
    ---
    
    ## Graph Flow Visualization
    
    ### Linear Graph (Our Example):
    
    ```
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │ add_one │
    └────┬────┘
         │
    ┌────▼────┐
    │ add_two │
    └────┬────┘
         │
    ┌────▼────┐
    │   END   │
    └─────────┘
    
    ```
    
    ### Multiple Nodes:
    
    ```
    START → process → validate → save → END
    
    ```
    
    Each arrow is an `add_edge()` call!
    
    ---
    
    ## Special Nodes: START and END
    
    ### START
    
    ```python
    graph.set_entry_point("first_node")
    # Equivalent to: graph.add_edge(START, "first_node")
    
    ```
    
    **Meaning:** Where to begin
    
    ### END
    
    ```python
    graph.add_edge("last_node", END)
    
    ```
    
    **Meaning:** Where to finish
    
    **Rule:** Every graph needs one entry point and at least one END!
    
    ---
    
    ## Example: String Processing Graph
    
    Let's build something more realistic:
    
    ```python
    from typing import TypedDict
    from langgraph.graph import StateGraph, END
    
    # State
    class TextState(TypedDict):
        text: str
    
    # Nodes
    def uppercase(state: TextState) -> TextState:
        return {"text": state["text"].upper()}
    
    def add_exclamation(state: TextState) -> TextState:
        return {"text": state["text"] + "!!!"}
    
    # Build graph
    graph = StateGraph(TextState)
    graph.add_node("uppercase", uppercase)
    graph.add_node("add_exclamation", add_exclamation)
    
    graph.set_entry_point("uppercase")
    graph.add_edge("uppercase", "add_exclamation")
    graph.add_edge("add_exclamation", END)
    
    # Run
    app = graph.compile()
    result = app.invoke({"text": "hello"})
    print(result)
    # Output: {'text': 'HELLO!!!'}
    
    ```
    
    **Flow:**
    
    ```
    "hello" → uppercase → "HELLO" → add_exclamation → "HELLO!!!"
    
    ```
    
    ---
    
    ## Common Patterns
    
    ### Pattern 1: Sequential Processing
    
    ```python
    graph.set_entry_point("step1")
    graph.add_edge("step1", "step2")
    graph.add_edge("step2", "step3")
    graph.add_edge("step3", END)
    
    # Flow: step1 → step2 → step3 → END
    
    ```
    
    ### Pattern 2: Multiple Inputs
    
    ```python
    class State(TypedDict):
        input1: str
        input2: str
        result: str
    
    def combine(state: State) -> State:
        return {"result": state["input1"] + state["input2"]}
    
    # Invoke with both inputs
    result = app.invoke({"input1": "hello", "input2": "world"})
    
    ```
    
    ### Pattern 3: Accumulation
    
    ```python
    class State(TypedDict):
        values: list
    
    def add_value(state: State) -> State:
        return {"values": state["values"] + [42]}
    
    # State grows: [] → [42] → [42, 42]
    
    ```
    
    ---
    
    ## Key Concepts Recap
    
    ### 1. State = Data Container
    
    ```python
    class State(TypedDict):
        field1: type
        field2: type
    
    ```
    
    ### 2. Node = Function
    
    ```python
    def node_name(state: State) -> State:
        # Read state, do work, return update
        return {"field": new_value}
    
    ```
    
    ### 3. Edge = Connection
    
    ```python
    graph.add_edge("from_node", "to_node")
    
    ```
    
    ### 4. Graph = State Machine
    
    ```python
    graph = StateGraph(State)
    graph.add_node("name", function)
    graph.add_edge("name", END)
    graph.set_entry_point("name")
    app = graph.compile()
    
    ```
    
    ---
    
    ## What We Haven't Covered Yet
    
    **This video:** Simple linear graphs
    
    - START → Node A → Node B → END
    
    **Next videos:**
    
    - **5.4:** Build complete example (not just concepts)
    - **5.5:** Real agent migration (TestCase)
    - **5.6:** Conditional edges (if/else routing)
    - **5.7:** Loops and retry logic
    
    **Don't worry!** We'll learn these step by step.
    
    ---
    
    ## Quick Exercise (Try This!)
    
    Modify the counter example to multiply instead of add:
    
    ```python
    def multiply_two(state: CounterState) -> CounterState:
        return {"count": state["count"] * 2}
    
    # Flow: start with 5 → add_one → multiply_two
    # Result: (5 + 1) * 2 = 12
    
    ```
    
    Try it yourself!
    
    ---
    
    ## Common Mistakes
    
    ### Mistake 1: Returning Entire State
    
    ```python
    # ❌ Don't do this
    def node(state: State) -> State:
        return {
            "field1": state["field1"],
            "field2": state["field2"] + 1,
            "field3": state["field3"]
        }
    
    # ✅ Do this (only what changed)
    def node(state: State) -> State:
        return {"field2": state["field2"] + 1}
    
    ```
    
    ### Mistake 2: Forgetting END
    
    ```python
    # ❌ Graph never finishes
    graph.add_edge("last_node", "nowhere")
    
    # ✅ Always end somewhere
    graph.add_edge("last_node", END)
    
    ```
    
    ### Mistake 3: No Entry Point
    
    ```python
    # ❌ Where to start?
    graph.add_node("node1", func1)
    
    # ✅ Always set entry
    graph.set_entry_point("node1")
    
    ```
    
    ---
    
    ## What's Next?
    
    Now that you understand the 3 core concepts:
    
    - ✅ State (data container)
    - ✅ Nodes (functions)
    - ✅ Edges (connections)
    
    In **5.4**, we'll build a **complete working graph** from scratch:
    
    - Multi-step workflow
    - Real problem solving
    - Not just concepts, actual implementation!
    
    Then in **5.5**, we'll migrate our **TestCase Agent** to LangGraph! 🚀
    
    ---
    
    ## Key Takeaways
    
    **LangGraph is Simple:**
    
    ```python
    # 3 things to remember:
    1. State = TypedDict (data)
    2. Node = function(state) -> state
    3. Edge = connection
    
    # That's it!
    
    ```
    
    **Building Blocks:**
    
    ```python
    graph = StateGraph(State)     # Create
    graph.add_node("name", func)  # Add nodes
    graph.add_edge("a", "b")      # Connect
    graph.set_entry_point("a")    # Start
    app = graph.compile()         # Build
    result = app.invoke(data)     # Run
    
    ```