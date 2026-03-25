- Langchain Introduction
    
    # What is Langchain?
    
    ## What We'll Cover
    
    Introduction to Langchain framework and why it exists
    
    ---
    
    ## What is Langchain?
    
    **Langchain** is an open-source framework for building LLM-powered applications.
    
    Think of it as a **toolkit** that simplifies common LLM tasks:
    
    - Chaining multiple LLM calls together
    - Managing prompts
    - Parsing LLM outputs
    - Integrating with external tools (APIs, databases)
    - Adding memory to conversations
    
    ---
    
    ## Why Langchain Exists?
    
    ### Problem Without Langchain:
    
    ```python
    # Our current approach (Basic Course)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    response = chat(messages)
    # Manual parsing, error handling, chaining...
    
    ```
    
    **Issues:**
    
    - Manual message formatting
    - No built-in retry logic
    - Hard to chain multiple LLM calls
    - No memory between calls
    - Reinventing the wheel for common patterns
    
    ### Solution With Langchain:
    
    ```python
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.chains import LLMChain
    
    # Langchain handles formatting, retries, parsing automatically
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run(user_input=requirement)
    
    ```
    
    **Benefits:**
    
    - Built-in prompt templates
    - Automatic retry logic
    - Easy chaining of operations
    - Memory support
    - Rich ecosystem of integrations
    
    ---
    
    ## What Langchain Provides
    
    ### 1. **Models** (LLM Wrappers)
    
    ```python
    from langchain.chat_models import ChatOpenAI, ChatAnthropic
    from langchain.llms import Ollama
    
    # Works with any provider using same interface
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    ```
    
    ### 2. **Prompts** (Template Management)
    
    ```python
    from langchain.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a QA engineer"),
        ("user", "Generate test cases for: {requirement}")
    ])
    
    ```
    
    ### 3. **Chains** (Sequencing Operations)
    
    ```python
    # Chain multiple steps together
    chain = prompt | llm | output_parser
    result = chain.invoke({"requirement": "login feature"})
    
    ```
    
    ### 4. **Memory** (Conversation History)
    
    ```python
    from langchain.memory import ConversationBufferMemory
    
    memory = ConversationBufferMemory()
    # Automatically tracks conversation history
    
    ```
    
    ### 5. **Agents** (Tool-using LLMs)
    
    ```python
    # LLM can call external tools (search, APIs, calculators)
    agent = create_agent(llm, tools=[search_tool, calculator])
    
    ```
    
    ---
    
    ## Langchain vs Our Current Approach
    
    | Feature | Our Approach (Basic Course) | Langchain |
    | --- | --- | --- |
    | LLM Calls | Manual `httpx` requests | Built-in wrappers |
    | Prompts | String formatting | Prompt templates |
    | Chaining | Manual function calls | Built-in chains |
    | Memory | Manual state management | Built-in memory |
    | Retries | Manual try-except | Automatic retries |
    | Parsing | Manual JSON parsing | Output parsers |
    
    ---
    
    ## When to Use Langchain?
    
    ### ✅ Use Langchain When:
    
    - Building complex multi-step workflows
    - Need memory/conversation history
    - Chaining multiple LLM calls
    - Using multiple external tools
    - Want built-in retry/error handling
    - Building production applications
    
    ### ❌ Skip Langchain When:
    
    - Simple single LLM call
    - Learning LLM basics (like we did!)
    - Prototyping quickly
    - Need full control over HTTP requests
    - Minimal dependencies required
    
    ---
    
    ## What We'll Build in This Section
    
    We'll migrate our **Basic Course agents** to Langchain:
    
    **Before (Vanilla Python):**
    
    ```
    src/agents/
    ├─ testcase_agent.py    # Manual LLM calls
    └─ log_analyzer.py      # Manual parsing
    
    ```
    
    **After (Langchain):**
    
    ```
    src/agents_v2/
    ├─ testcase_langchain.py    # Using Langchain chains
    └─ log_analyzer_langchain.py # Using Langchain parsers
    
    ```
    
    **Purpose:** Learn Langchain basics before moving to **LangGraph** (next section)
    
    ---
    
    ## Key Takeaway
    
    **Langchain = Productivity Framework for LLM Apps**
    
    It doesn't make agents "smarter" - it makes development **faster** and **more maintainable**.
    
    Think of it like:
    
    - We learned Python basics → Now we learn frameworks (Django/Flask)
    - We learned LLM basics → Now we learn frameworks (Langchain)