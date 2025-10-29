# CodeGenesis

An autonomous, multi-agent AI software development team powered by LangGraph. This project uses a "divide and conquer" strategy with specialized AI agents to turn a single user prompt into a fully coded, debugged, and functional software project.

## Core Concept

CodeGenesis simulates a software development team with distinct roles:

1. **Planner:** The "Product Manager" who clarifies the user's request into a high-level plan.

2. **Architect:** The "Tech Lead" who designs the software, breaking the plan into a detailed, step-by-step `TaskPlan` (e.g., file structure, what each file should do).

3. **Coder:** The "Developer" who executes the `TaskPlan` one file at a time, using tools to write and save code.

4. **Debugger:** The "QA Engineer" who reviews the entire project, runs tests (or analyzes the code for bugs), and decides if the project is "Approved" or needs fixes.

If bugs are found, the Debugger generates a new `TaskPlan` with the required fixes, which is sent back to the Coder. This "Code $\rightarrow$ Debug $\rightarrow$ Fix" loop continues until the project is approved.

## Agent Workflow
```
graph TD
    A[User Prompt] --> B(Planner Agent);
    B -- Plan --> C(Architect Agent);
    C -- TaskPlan --> D(Coder Agent);
    D -- status: IN_PROGRESS --> D;
    D -- status: DONE --> E(Debugger Agent);
    E -- status: BUGS_FOUND --> C;
    E -- status: APPROVED --> F[✅ Project Approved];
```

## The Agent Team & Tech Stack

This project uses a Multi-LLM strategy to leverage the best model for each task:

* **Planner & Architect (OpenAI `gpt-4o`):**

Uses `openai_llm` for high-level reasoning, planning, and structuring the `TaskPlan`.

* **Coder & Debugger (Anthropic `claude-3-5-sonnet`):**

Uses `anthropic_llm` for its strong code generation, large context window, and robust debugging capabilities.

These agents are built using `langgraph.prebuilt.create_react_agent` and are equipped with file system tools (`read_file`, `write_file`, `list_file`) and a command-line tool (`run_cmd`).

## Setup & Installation

1. **Clone the repository:**
```
git clone [https://github.com/your-username/code_genesis.git](https://github.com/your-username/code_genesis.git)
cd code_genesis
```

2. **Install dependencies using `uv`:**
*(If you don't have `uv`, install it first: `pip install uv`)*
```
uv sync
```

*(Alternatively, if you use `pip`):*
```
pip install -r requirements.txt
```

3. Set up environment variables:
*Create a `.env` file in the project root.*
```
cp .env.example .env

```
*(If `.env.example` doesn't exist, just create `.env` and add the following):*
```
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-..."
```

## How to Run

The main entrypoint is `main.py`. You can run it directly from your terminal:
```
python main.py
```

By default, the script will prompt you for a project idea. You can also pass the prompt directly as an argument (if you modify `main.py` to accept `sys.argv`):
```
python main.py "Build a simple web-based pomodoro timer in HTML, CSS, and JS"
```

The agent will start its work, creating a `generated_project/` directory and building your software inside it. You can follow its progress in the console.

## Project Structure
```
CODE_GENESIS/
│
├── .venv/                  # Python virtual environment
├── agent/                  # Core agent package
│   ├── __init__.py
│   ├── graph.py            # ★ Main LangGraph definition (nodes, edges, and graph compilation)
│   ├── prompt.py           # All system prompts for the agents (Planner, Coder, etc.)
│   ├── states.py           # Pydantic models for graph state (AgentState, Plan, TaskPlan)
│   └── tools.py            # Tool definitions (read_file, write_file, run_cmd)
│
├── .env                    # Secret API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
├── .gitignore
├── .python-version
├── LICENSE
├── main.py                 # ★ Entrypoint to run the agent graph
├── pyproject.toml          # Project metadata and dependencies for uv/pip
├── README.md               # This file
├── requirements.txt
└── uv.lock                 # uv lockfile
```
## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.