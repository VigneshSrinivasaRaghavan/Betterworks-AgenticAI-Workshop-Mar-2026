# What is MCP?

**MCP — Model Context Protocol**

An open standard protocol (by Anthropic, 2024)
that defines how AI models connect to external tools and data sources
in a consistent, reusable way.

**What MCP is:**
- A communication protocol (like HTTP — but for AI tools)
- A standard interface between an LLM and any external capability
- Provider-agnostic — works with OpenAI, Anthropic, Gemini, local models

**What MCP is NOT:**
- Not a library
- Not a framework
- Not a specific tool or product

**One protocol → any LLM talks to any tool. No custom glue code.**

---

# MCP vs Traditional Tool Integration

| | Traditional | MCP |
|---|---|---|
| Integration per tool | Custom code per LLM | One standard schema |
| Reusability | Low — tied to one provider | High — works with any LLM |
| Discovery | Hardcoded in app | LLM reads the schema at runtime |
| Maintenance | Update every integration | Update one server |
| Examples | OpenAI function calling (custom) | Browser, DB, files — all via MCP |

**Key shift:**
Before MCP → developer defines tools for a specific LLM
After MCP → server exposes tools, any LLM can discover and use them

---

# MCP Architecture — Three Roles

**Every MCP interaction has three participants:**

**1. MCP Host**
The application running the LLM.
Example: Cursor IDE, your LangGraph agent, Claude Desktop.
Responsible for: managing connections to MCP servers.

**2. MCP Client**
Lives inside the host.
Maintains a 1-to-1 connection with one MCP server.
Responsible for: sending requests, receiving responses.

**3. MCP Server**
A separate process (or service) that exposes tools.
Example: Playwright MCP server, a database MCP server.
Responsible for: declaring what tools it has + executing them.

---

# MCP Architecture — Visual

    ┌─────────────────────────────────┐
    │  MCP Host (your LangGraph app)  │
    │                                 │
    │  ┌───────────────────────────┐  │
    │  │  MCP Client               │  │
    │  │  (manages connection)     │  │
    │  └────────────┬──────────────┘  │
    └───────────────┼─────────────────┘
                    │  stdio / SSE / HTTP
                    ▼
    ┌─────────────────────────────────┐
    │  MCP Server (Playwright)        │
    │                                 │
    │  Tools:                         │
    │  • browser_navigate             │
    │  • browser_click                │
    │  • browser_snapshot             │
    │  • browser_fill                 │
    │  • ... 20+ more                 │
    └─────────────────────────────────┘

**Transport options:** stdio (local process), SSE, HTTP

---

# How MCP Servers Expose Tools

**Three steps a server does:**

**Step 1 — Declare Tools**
The server publishes a list of tools it can perform.
Each tool has: name, description, input schema (JSON Schema).

**Step 2 — LLM Reads the Schema**
When the host connects, the client fetches the tool list.
The LLM receives all tool descriptions.
The LLM now knows: what tools exist, what parameters they need.

**Step 3 — LLM Decides to Call**
Based on the user instruction and the tool descriptions,
the LLM decides which tool to call and with what arguments.
The MCP client sends the call → server executes → returns result.

**No hardcoding. The LLM reads the menu and orders.**

---

# The Tool Schema — What the LLM Sees

**Every MCP tool is described by a JSON schema:**

    {
      "name": "browser_navigate",
      "description": "Navigate to a URL in the browser.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "The URL to navigate to."
          }
        },
        "required": ["url"]
      }
    }

**The LLM reads the description and decides:**
"The user wants to open a login page.
I should call browser_navigate with url = '<https://example.com/login>'"

**The description IS the instruction to the LLM.**
Well-written descriptions = smarter tool selection.

---

# The Full Request-Response Flow

    1. Agent receives task:
       "Go to the login page and enter valid credentials"

    2. LLM reads tool schemas from Playwright MCP server:
       — browser_navigate, browser_snapshot, browser_fill, browser_click

    3. LLM decides: call browser_navigate(url="<https://example.com/login>")

    4. MCP Client sends request → Playwright MCP Server executes

    5. Server navigates browser → returns page snapshot (ARIA tree)

    6. LLM reads snapshot → decides: call browser_fill(value="user@test.com")

    7. Continues tool calls until task is complete

    8. LLM returns final result to agent

**This loop is the core of every MCP-powered agent.**

---

# Key Takeaways

- MCP is a protocol — not a library, not a framework
- It solves the N×M integration problem: one standard for all LLMs and tools
- Three roles: Host (your app), Client (connection manager), Server (tool provider)
- Servers expose tools via JSON schema — name, description, input schema
- The LLM reads the schema and autonomously decides which tool to call
- Tool descriptions are critical — they are the LLM's instructions
- Transport options: stdio (local), SSE, HTTP
- Two MCP servers are already live in this project — Playwright and Cursor browser
- Everything we build next (Sections 2–6) runs on top of this protocol