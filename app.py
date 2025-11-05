# app.py

import pathlib
import shutil
from typing import Any, Dict

import streamlit as st

from agent.graph import agent, init_project_root

PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"


def list_files(base: pathlib.Path) -> list[pathlib.Path]:
  if not base.exists():
    return []
  return [p for p in base.rglob("*") if p.is_file()]


st.set_page_config(page_title="AI Engineering Project Planner", layout="wide")
st.title("🧪 AI Engineering Project Planner (LangGraph)")

with st.sidebar:
  st.header("⚙️ Settings")
  recursion_limit = st.number_input(
    "Recursion limit", min_value=10, max_value=500, value=100, step=10
  )
  clear_before_run = st.checkbox(
    "Clear generated_project before run", value=False,
    help="Deletes the existing generated_project folder before execution."
  )

st.markdown(
  "Enter a project idea. The system will plan, architect tasks, implement files, and run a debug pass."
)

user_prompt = st.text_area(
  "Project prompt",
  placeholder="Build a colourful modern todo app in HTML, CSS, and JS",
  height=140,
)

col_run, col_refresh = st.columns([1,1])
run_clicked = col_run.button("🚀 Run Planner")
refresh_clicked = col_refresh.button("🔄 Refresh File List")

status_placeholder = st.empty()

init_project_root()

if run_clicked and user_prompt.strip():
  if clear_before_run and PROJECT_ROOT.exists():
    shutil.rmtree(PROJECT_ROOT)
    init_project_root()

  status_placeholder.info("Running agent… this can take a minute depending on your LLMs.")

  try:
    result: Dict[str, Any] = agent.invoke(
      {"user_prompt": user_prompt},
      {"recursion_limit": int(recursion_limit)}
    )
    status_placeholder.success("Done ✅")

    st.subheader("Final State")
    st.json(result)

    plan = result.get("plan")
    task_plan = result.get("task_plan")
    last_output = result.get("last_output")
    status = result.get("status")

    if status:
      st.info(f"Status: {status}")

    with st.expander("📝 Plan", expanded=False):
      if plan:
        st.json(plan)
      else:
        st.write("No plan found.")

    with st.expander("🧱 Task Plan", expanded=False):
      if task_plan:
        st.json(task_plan)
      else:
        st.write("No task plan found.")

    with st.expander("📤 Last Output (e.g., coder/debugger)", expanded=False):
      if last_output:
        st.code(str(last_output))
      else:
        st.write("No last output yet.")

  except Exception as e:
    status_placeholder.error(f"Error: {e}")

st.subheader("📁 generated_project contents")
files = list_files(PROJECT_ROOT)
if not files:
  st.caption("No files yet. Run the planner to generate your project.")
else:
  for p in files:
    rel = p.relative_to(PROJECT_ROOT)
    with st.expander(str(rel), expanded=False):
      try:
        text = p.read_text(encoding="utf-8")
        st.code(text)
      except Exception:
        st.write("(Binary or unreadable file)")
