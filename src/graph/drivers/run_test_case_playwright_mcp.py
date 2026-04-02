"""
TestCase Generator + Playwright MCP Executor Driver

Generates test cases from a requirement file, then executes each
test case in a real browser using the Playwright MCP agent.

Run:
  python -m src.graph.drivers.run_test_case_playwright_mcp
  python -m src.graph.drivers.run_test_case_playwright_mcp data/requirements/payment_checkout.txt https://target-app.com
"""
import sys
import uuid
import asyncio
from pathlib import Path
from src.graph.test_case_playwright_mcp.graph import build_graph

ROOT = Path(__file__).resolve().parents[3]


def display_test_cases(test_cases: list):
    print("\n" + "=" * 60)
    print(f"Generated {len(test_cases)} Test Case(s):")
    print("=" * 60)
    for tc in test_cases:
        print(f"\n  [{tc.get('priority', '?')}] {tc.get('id', '?')} — {tc.get('title', '?')}")
        for step in tc.get("steps", []):
            print(f"    • {step}")
        print(f"    Expected: {tc.get('expected', '?')}")
    print("=" * 60)


def display_execution_results(results: list):
    print("\n" + "=" * 60)
    print("Playwright Execution Results:")
    print("=" * 60)
    for r in results:
        status_icon = "✓" if r["status"] == "PASS" else "✗" if r["status"] == "FAIL" else "!"
        print(f"\n  [{status_icon}] {r['id']} — {r['title']}")
        print(f"      Status:    {r['status']}")
        if r.get("actual"):
            print(f"      Actual:    {r['actual']}")
        if r.get("reasoning"):
            print(f"      Reasoning: {r['reasoning']}")
    print("=" * 60)


async def main():
    app = build_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n" + "=" * 60)
    print("TestCase Generator + Playwright MCP Executor")
    print("=" * 60)
    print(f"Session ID: {thread_id[:8]}...")

    # Read args: optional requirement file path and target URL
    requirement = ""
    target_url = ""

    if len(sys.argv) > 1:
        req_path = Path(sys.argv[1])
        if not req_path.exists():
            print(f"File not found: {req_path}")
            return
        requirement = req_path.read_text(encoding="utf-8")
        print(f"Requirement file: {req_path.name}")

        # Auto-detect target URL from requirements file if line starts with "Target URL:"
        for line in requirement.splitlines():
            if line.strip().lower().startswith("target url:"):
                target_url = line.split(":", 1)[-1].strip()
                print(f"Target URL (from requirements): {target_url}")
                break

    if len(sys.argv) > 2:
        target_url = sys.argv[2]
        print(f"Target URL (from CLI): {target_url}")
    elif not target_url:
        target_url = input("\nEnter target URL to test against (e.g. https://example.com): ").strip()

    init_state = {
        "requirement": requirement,
        "conversation_history": [],
        "past_patterns": "",
        "retrieved_context": "",
        "test_cases": [],
        "errors": [],
        "validation_status": "pending",
        "retry_count": 0,
        "target_url": target_url,
        "execution_results": []
    }

    print("\nRunning graph...\n")
    result = await app.ainvoke(init_state, config=config)

    if result.get("errors"):
        print("Errors:", result["errors"])

    if result.get("test_cases"):
        display_test_cases(result["test_cases"])

    if result.get("execution_results"):
        display_execution_results(result["execution_results"])


if __name__ == "__main__":
    asyncio.run(main())
