# LangGraph Report Generator

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-latest-green)
![Claude](https://img.shields.io/badge/Claude-Anthropic-orange)

An LLM workflow built with LangGraph and Claude. Given any topic, the system plans a set of sub-topics, writes each section in parallel, and assembles everything into a formatted markdown report saved as `report.md`.

---

## Architecture

The workflow follows a **planner → fan-out → parallel writers → assembler** pattern:

```
START
  │
  ▼
planner_node          ← breaks topic into 5–8 sub-topics
  │
  ▼
fan_out_to_writers    ← conditional edge using Send() for dynamic fan-out
  │
  ├──▶ writer_node (sub-topic 1) ─┐
  ├──▶ writer_node (sub-topic 2) ─┤
  ├──▶ writer_node (sub-topic 3) ─┼──▶ assemble_report_node ──▶ END
  ├──▶ writer_node (sub-topic 4) ─┤
  └──▶ writer_node (sub-topic N) ─┘
```

Each writer node runs concurrently and contributes its section to the shared state via a reducer, after which the assembler node combines them into the final report.

---

## Key Concepts Demonstrated

- **`StateGraph` with `TypedDict`** — defines the shared state schema that flows through all nodes
- **`Send` for dynamic fan-out** — the conditional edge function creates one `Send` object per sub-topic at runtime, enabling a variable number of parallel branches
- **State reducers (`operator.add`)** — the `completed_sections` field uses a reducer to safely merge concurrent writes from multiple parallel writer nodes into a single list
- **Conditional edges** — routing logic that inspects planner output and dispatches to writer nodes dynamically
- **Structured outputs with Pydantic** — `llm.with_structured_output()` ensures reliable, type-safe JSON parsing from LLM responses

---

## Project Structure

```
report_generator/
├── main.py        # Entry point — compiles and invokes the graph
├── graph.py       # Graph definition, nodes, edges, and routing logic
├── nodes.py       # Node implementations: planner, writer, assembler
└── state.py       # Shared state schema (ReportState TypedDict)
```

---

## Setup & Usage

**Prerequisites**
- Python 3.11+
- An Anthropic API key

**Installation**

```bash
git clone https://github.com/your-username/langgraph-report-generator.git
cd langgraph-report-generator

python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate

pip install langgraph langchain langchain-anthropic python-dotenv
```

**Configuration**

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-haiku-4-5
```

`ANTHROPIC_MODEL` accepts any model from the Anthropic API (e.g. `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`). More capable models will produce higher quality reports at increased cost.

**Run**

```bash
python main.py
```

To change the topic, edit the `topic` variable in `main.py`. The final report is written to `report.md` in the project root.

---

## Example Output

For the topic *"An Overview of the Rust Programming Language"*, the planner node produced the following sections:

1. Historical Development and Design Philosophy of Rust
2. Core Language Features and Syntax
3. Memory Safety and Ownership System
4. Error Handling and Result Types
5. Concurrency and Performance Capabilities
6. Ecosystem and Popular Libraries
7. Real-World Applications and Use Cases

Each section is written in parallel and assembled into a single markdown report. Here is an excerpt:

```markdown
# An Overview of the Rust Programming Language

## Memory Safety and Ownership System
Rust's most distinctive feature is its innovative approach to memory safety
through its ownership system, which eliminates entire classes of bugs without
requiring garbage collection. This system represents a fundamental shift in
how programming languages handle memory management, providing developers with
both safety and performance.

At the core of Rust's design is the concept of ownership. Every value in Rust
has exactly one owner responsible for deallocating it when it's no longer
needed. When ownership transfers to another binding, the original variable can
no longer be used — a concept called "moving"...
```

---

## What I Learned
This project helped with better understanding the fundamentals of LangGraph. One of the core components of LangGraph is being able to create graphs of workflows that utilize LLMs in a more structured and modular manner. As LLMs emerge as a more established technology in a wide range of industries, it's important to understand how to utilize LLMs within existing ecosystems.

By splitting the work into three distinct nodes (planner, writer, and assembler), I was able to better break down the problem I attempted to solve into smaller chunks. Engineering prompts for each node is a much more manageable and trivial task than writing up a singular, monolithic prompt. If I encountered an aspect of the report generation that wasn't working as intended, I could better identify which component would need changes.

I also learned how LLMs can interact with structured outputs. Coming from using LLMs purely through chat interfaces such as [claude.ai](claude.ai) and [chatgpt.com](chatgpt.com), I was used to the convention of the output strictly being Markdown text that the LLM sent back. Using ```with_structured_output()``` allowed me to structure an LLM's output better, and adds a new dimension of structure to how I can have LLMs interact with my prompts.