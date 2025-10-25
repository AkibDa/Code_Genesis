from dotenv import load_dotenv # type: ignore
from langchain_groq import ChatGroq # type: ignore
from langgraph.constants import END # type: ignore
from langgraph.graph import StateGraph # type: ignore

from prompt import *
from states import *

_ = load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

def planner_agent(state: dict) -> dict:
  """Converts user prompt into a structured Plan."""
  user_prompt = state["user_prompt"]
  resp = llm.with_structured_output(Plan).invoke(
    planner_prompt(user_prompt)
  )
  if resp is None:
    raise ValueError("Planner did not return a valid response.")
  return {"plan": resp}

def architect_agent(state: dict) -> dict:
  """Creates TaskPlan from Plan."""
  plan: Plan = state["plan"]
  resp = llm.with_structured_output(TaskPlan).invoke(
    architect_prompt(plan=plan.model_dump_json())
  )
  if resp is None:
    raise ValueError("Planner did not return a valid response.")

  resp.plan = plan
  print(resp.model_dump_json())
  return {"task_plan": resp}

def coder_agent(state: dict) -> dict:
  """LangGraph tool-using coder agent."""
  coder_state: CoderState = state.get("coder_state")
  if coder_state is None:
    coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

  steps = coder_state.task_plan.implementation_steps
  if coder_state.current_step_idx >= len(steps):
    return {"coder_state": coder_state, "status": "DONE"}

  current_task = steps[coder_state.current_step_idx]
  existing_content = read_file.run(current_task.filepath)

  system_prompt = coder_system_prompt()
  user_prompt = (
    f"Task: {current_task.task_description}\n"
    f"File: {current_task.filepath}\n"
    f"Existing content:\n{existing_content}\n"
    "Use write_file(path, content) to save your changes."
  )

  coder_tools = [read_file, write_file, list_files, get_current_directory]
  react_agent = create_react_agent(llm, coder_tools)

  react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}]})

  coder_state.current_step_idx += 1
  return {"coder_state": coder_state}

# response = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))

# print(response)

graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", code_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
  "coder",
  lambda s: "END" if s.get("status") == "DONE" else "coder",
  {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent = graph.compile()

if __name__ == "__main__":
  user_prompt = "Create a simple calculator web application"
  
  result = agent.invoke({"user_prompt": user_prompt})
  print(result)