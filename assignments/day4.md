# Day 4 Assignment

## Assignment 1 - Log Analyzer Agent

Build an agent `log_analyzer` that reads a log file and produces a structured analysis with technical details, a JSON summary, and a plain-English executive summary — all in a single LLM call.

**High-level steps**

1. **Pick the log file** — accept a CLI argument (file path); if none given, auto-pick the first `.log` or `.txt` file from `data/logs/`
2. **Build the prompt** — system prompt should instruct the LLM to act as a DevOps engineer and return three distinct sections in one response:
   - A narrative technical analysis (errors, root causes, impact, recommendations)
   - A structured JSON block fenced with ` ```json ` containing fields: `summary`, `error_count`, `critical_errors`, `root_causes`, `affected_systems`, `recommendations`, `severity`
   - A plain-English executive summary after a `---EXECUTIVE---` marker
3. **Single LLM call** — pass system + user messages to `chat()`
4. **Parse the response** — split on ` ```json ` and `---EXECUTIVE---` to extract the three parts
5. **Save outputs** to `outputs/log_analyzer/`:
   - `<stem>_analysis.txt` — technical report
   - `<stem>_analysis.json` — parsed JSON summary
   - `<stem>_executive.txt` — executive summary

Reference implementation: `src/agents/log_analyzer.py`


## Assignment 2 - Edge / Negative Testcase Generator

Implement an agent `edgecase_agent` that reads a requirement text (single file) and produces a JSON array of test cases emphasizing edge and negative scenarios in addition to normal cases.

Requirements

- Input: a requirement text file from `data/requirements` (CLI: `--input PATH`).
- Output: a JSON array (printed or returned) and a CSV `outputs/testcase_generated/test_cases.csv`.
- Each test case object must include: `id`, `title`, `steps`, `expected`, `priority`, `tags`.
- At least 6 and at most 12 test cases. At least 30% must be tagged as `edge` or `negative`.

Expected output (JSON schema per case)

{
  "id": "TC-001",
  "title": "Short test title",
  "steps": ["step 1", "step 2"],
  "expected": "Expected result",
  "priority": "High|Medium|Low",
  "tags": ["edge"|"negative"|"happy"],
}

CSV columns: TestID, Title, Steps, Expected, Priority, Tags, Likelihood
