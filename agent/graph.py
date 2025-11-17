import pathlib
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_core.globals import set_verbose, set_debug
from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from .prompt import *
from .states import *
from .tools import *
from .utility import *

# --- Load Env and Set Debugging ---
_ = load_dotenv()
set_debug(True)
set_verbose(True)

# --- Define LLM and Tools ---
llm = ChatGroq(model="openai/gpt-oss-120b", 
               timeout=60, 
               max_retries=3,
               temperature=0)

# Define tools for each agent
coder_tools = [read_file, write_file, list_file, get_current_directory, run_cmd]
debugger_tools = [read_file, list_file, get_current_directory, run_cmd]

# --- Create Agents (Outside Nodes) ---
coder_react_agent = create_react_agent(
    model=llm,
    tools=coder_tools
)
debugger_react_agent = create_react_agent(
    model=llm,
    tools=debugger_tools
)

# --- Define Graph State ---
class AgentState(TypedDict):
    user_prompt: str
    plan: Optional[Plan]
    task_plan: Optional[TaskPlan]
    coder_state: Optional[CoderState]
    status: Optional[str]
    last_output: Optional[str]
    last_error: Optional[str]  # <-- NEW: For self-correction

# === Define Graph Nodes ===

def planner_agent(state: AgentState) -> AgentState:
    print("\n--- PLANNER AGENT ---")
    new_state = dict(state)
    user_prompt = new_state.get("user_prompt")
    if not user_prompt:
        raise ValueError("planner_agent expects 'user_prompt' in state.")
    resp = invoke_structured(llm, Plan, planner_prompt(user_prompt))
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    new_state["plan"] = resp
    return new_state

def architect_agent(state: AgentState) -> AgentState:
    print("\n--- ARCHITECT AGENT ---")
    new_state = dict(state)
    plan: Plan = new_state.get("plan")
    if plan is None:
        raise ValueError("architect_agent expects 'plan' in state.")
    resp = invoke_structured(
        llm, TaskPlan, architect_prompt(plan=plan.model_dump_json(indent=2))
    )
    if resp is None:
        raise ValueError("Architect did not return a valid response.")
    resp.plan = plan  # type: ignore
    print("\n[Architect Output]\n", resp.model_dump_json(indent=2))
    new_state["task_plan"] = resp
    return new_state

def coder_agent(state: AgentState) -> AgentState:
    print("\n--- CODER AGENT ---")
    new_state = dict(state)
    
    # Get and clear the last error to prevent re-using it
    last_error = new_state.pop("last_error", None)

    # 1. Setup Coder State
    coder_state: Optional[CoderState] = new_state.get("coder_state")
    if coder_state is None:
        print("Coder: Starting new task plan.")
        if "task_plan" not in new_state:
            raise ValueError("coder_agent expects 'task_plan' in state.")
        coder_state = CoderState(task_plan=new_state["task_plan"], current_step_idx=0)
    else:
        print(f"Coder: Continuing at step {coder_state.current_step_idx}")

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        print("Coder: All steps complete.")
        new_state["coder_state"] = coder_state
        new_state["status"] = "DONE"
        return new_state

    current_task = steps[coder_state.current_step_idx]
    print(f"\n[Coder Task {coder_state.current_step_idx + 1}/{len(steps)}]: {current_task.filepath}")
    print(f"[Task Description]: {current_task.task_description}")

    try:
        existing_content = read_file(current_task.filepath)
    except Exception:
        existing_content = "File not found or is empty."

    # 2. Build Correction Prompt (if applicable)
    error_correction_prompt = ""
    if last_error:
        print(f"\n[Coder RETRY]: Retrying step with error info: {last_error}")
        error_correction_prompt = (
            "Your previous attempt on this task failed. You must correct your action.\n"
            f"ERROR: {last_error}\n"
            "REMINDER: Review the available tools and their usage. "
            "The *only* tools available are: `read_file`, `write_file`, `list_file`, `get_current_directory`, `run_cmd`.\n"
            "Do not use prefixes like `repo_browser`.\n"
            "--- Please try the task again ---\n\n"
        )

    user_prompt = (
        f"{error_correction_prompt}"
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n\n"
        "Remember to use `write_file(path, content)` to save your *full* and *complete* changes."
    )

    # 3. Run Agent with Error Handling
    try:
        llm_response_dict = invoke_messages(
            coder_react_agent,
            [SystemMessage(content=coder_system_prompt()), HumanMessage(content=user_prompt)]
        )
        
        # --- SUCCESS ---
        final_message = llm_response_dict.get('messages', [])[-1] if isinstance(llm_response_dict, dict) else None
        llm_output = (final_message.content if final_message else str(llm_response_dict))

        print(f"\n[Coder Output]:\n{llm_output}")

        coder_state.current_file_content = llm_output
        coder_state.current_step_idx += 1  # <-- IMPORTANT: Increment index on success

        new_state["coder_state"] = coder_state
        new_state["status"] = "IN_PROGRESS"
        new_state["last_output"] = coder_state.current_file_content
        # new_state["last_error"] is already cleared

    except Exception as e:
        # --- FAILURE ---
        error_str = str(e)
        print(f"\n[Coder ERROR]: {error_str}")

        if "Tool call validation failed" in error_str or "Tool use failed" in error_str:
            # Persist the error for the next loop
            new_state["last_error"] = error_str
            new_state["status"] = "IN_PROGRESS"  # Loop back to coder
            new_state["coder_state"] = coder_state  # DO NOT increment index
            new_state["last_output"] = f"Error occurred: {error_str}"
        else:
            # A different, unexpected error
            raise e

    return new_state

def debugger_agent(state: AgentState) -> AgentState:
    print("\n--- DEBUGGER AGENT ---")
    new_state = dict(state)
    
    # Get and clear the last error
    last_error = new_state.pop("last_error", None)

    if "plan" not in new_state:
        raise ValueError("debugger_agent expects 'plan' in state.")

    plan_json = new_state["plan"].model_dump_json(indent=2)
    
    # Build Correction Prompt
    error_correction_prompt = ""
    if last_error:
        print(f"\n[Debugger RETRY]: Retrying with error info: {last_error}")
        error_correction_prompt = (
            "Your previous attempt to debug failed. You must correct your action.\n"
            f"ERROR: {last_error}\n"
            "REMINDER: Review the available tools. The *only* tools available are: `read_file`, `list_file`, `get_current_directory`, `run_cmd`.\n"
            "Do not use prefixes like `repo_browser`.\n"
            "--- Please try to debug the project again ---\n\n"
        )

    debug_prompt = (
        f"{error_correction_prompt}"
        f"{debugger_user_prompt(original_plan=plan_json)}"
    )

    # Run Agent with Error Handling
    try:
        llm_response_dict = invoke_messages(
            debugger_react_agent,
            [SystemMessage(content=debugger_system_prompt()), HumanMessage(content=debug_prompt)]
        )
        
        # --- SUCCESS ---
        bug_report = llm_response_dict.get('messages', [])[-1].content
        print(f"\n[Debugger Bug Report]:\n{bug_report}")

        if bug_report.strip() == "LGTM":
            print("\n[Debugger Status]: LGTM! Project Approved.")
            new_state["status"] = "APPROVED"
            return new_state
        else:
            print("\n[Debugger Status]: Bugs found. Generating fix plan...")
            fix_prompt = debugger_fix_prompt(
                bug_report=bug_report,
                original_plan=plan_json
            )
            fix_plan = invoke_structured(llm, TaskPlan, fix_prompt)

            print(f"\n[Debugger Fix Plan]:\n{fix_plan.model_dump_json(indent=2)}")

            new_state["task_plan"] = fix_plan
            new_state["coder_state"] = None
            new_state["status"] = "BUGS_FOUND"
            new_state["last_output"] = bug_report
            return new_state

    except Exception as e:
        # --- FAILURE ---
        error_str = str(e)
        print(f"\n[Debugger ERROR]: {error_str}")

        if "Tool call validation failed" in error_str or "Tool use failed" in error_str:
            # Persist the error for the next loop
            new_state["last_error"] = error_str
            new_state["status"] = "DEBUGGER_ERROR"  # <-- NEW STATUS
            new_state["last_output"] = f"Error occurred: {error_str}"
            return new_state
        else:
            # A different, unexpected error
            raise e

# === Define Graph ===
graph = StateGraph(AgentState)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)
graph.add_node("debugger", debugger_agent)

graph.set_entry_point("planner")

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")

# Coder loop:
# - If status is "DONE", go to "debugger"
# - Otherwise (e.g., "IN_PROGRESS"), loop back to "coder"
# This now handles both success (incremented index) and failure (same index + last_error)
graph.add_conditional_edges(
    "coder",
    lambda s: "debugger" if s.get("status") == "DONE" else "coder",
    {"debugger": "debugger", "coder": "coder"}
)

# Debugger loop:
# - If "BUGS_FOUND", go to "coder" to fix them
# - If "APPROVED", end the graph
# - If "DEBUGGER_ERROR", loop back to "debugger" to retry
graph.add_conditional_edges(
    "debugger",
    lambda s: "coder" if s.get("status") == "BUGS_FOUND" 
              else "debugger" if s.get("status") == "DEBUGGER_ERROR" 
              else "END",
    {"coder": "coder", "debugger": "debugger", "END": END}
)

agent = graph.compile()


if __name__ == "__main__":
    init_project_root()
    print(f"Project root initialized at: {pathlib.Path.cwd() / 'generated_project'}")
    
    result = agent.invoke(
        {"user_prompt": "Build a colourful modern todo app in html css and js"},
        {"recursion_limit": 100}
    )
    print("\n✅ Final State:\n", result)