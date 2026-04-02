"""
  1. Connect to Playwright MCP server via stdio
  2. List all available browser tools (what the LLM sees)
  3. Manually call browser_navigate and browser_snapshot

Run: python -m src.graph.drivers.run_mcp_connect
"""
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

# --- Playwright MCP Server Config ---
# command: how to start the MCP server process
# args: arguments passed to the command
# transport: how the client talks to the server (stdio = local subprocess)
PLAYWRIGHT_SERVER = {
    "playwright": {
        "command": "npx",
        "args": ["-y", "@playwright/mcp@latest"],
        "transport": "stdio",
    }
}


async def list_tools(client: MultiServerMCPClient):
    """Fetch and display all tools exposed by the MCP server."""
    tools = await client.get_tools()

    print(f"\nTotal tools available: {len(tools)}")
    print("=" * 60)
    for tool in tools:
        desc = tool.description[:70] + "..." if len(tool.description) > 70 else tool.description
        print(f"  {tool.name:<35} {desc}")
    print("=" * 60)

    return tools


async def demo_navigate_and_snapshot(tools: list):
    """Navigate to a URL and print the page ARIA snapshot."""

    navigate_tool = next((t for t in tools if t.name == "browser_navigate"), None)
    snapshot_tool = next((t for t in tools if t.name == "browser_snapshot"), None)

    if not navigate_tool or not snapshot_tool:
        print("Required tools not found!")
        return

    # Step 1: Navigate
    url = "https://www.saucedemo.com/"
    print(f"\nCalling browser_navigate → url: {url}")
    nav_result = await navigate_tool.ainvoke({"url": url})
    print(f"Result: {nav_result}")

    # Step 2: Snapshot — returns ARIA tree (what the LLM reads to understand the page)
    print("\nCalling browser_snapshot...")
    snapshot_result = await snapshot_tool.ainvoke({})
    snapshot_text = str(snapshot_result)

    print("\nPage ARIA Snapshot (first 600 chars):")
    print("=" * 60)
    print(snapshot_text[:600] + ("..." if len(snapshot_text) > 600 else ""))
    print("=" * 60)


async def main():
    print("\n" + "=" * 60)
    print("  Section 2 — MCP to LangChain Connection Demo")
    print("=" * 60)

    print("\nStarting Playwright MCP server (via npx)...")
    print("This may take a few seconds on first run...\n")

    # v0.2.x API — no context manager, just await get_tools()
    client = MultiServerMCPClient(PLAYWRIGHT_SERVER)
    await client.get_tools()  # initialises the connection

    print("Connected to Playwright MCP server!")

    # Step 1: List all tools
    tools = await list_tools(client)

    # Step 2: Navigate + snapshot demo
    await demo_navigate_and_snapshot(tools)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
