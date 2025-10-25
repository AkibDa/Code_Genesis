def planner_prompt(user_prompt: str) -> str:
  PLANNER_PROMPT = f"""
You are the PLANNER agent. Convert the user prompt into a COMPLETE engineering project plan

User request: {user_prompt}
"""
  return PLANNER_PROMPT

def architect_prompt(plan: str) -> str:
  ARCHITECT_PROMPT = f"""
You are the ARCHITECT agent. Given this project plan, break it down into explicit engineering tasks.

RULES:
- For each FILE in the plan, create one or more IMPLEMENTATION TASKS.
- In each task description:
  * Specify exactly what to implement.
  * Name the variables, functions, classes, and components to be defined.
  * Mention how this task depends on or will be used by previous tasks.
  * Include integration details: imports, expected function signatures, data flow.
- Order tasks so that dependencies are implemented first.
- Each step must be SELF-CONTAINED but also carry FORWARD the relevant context from earlier tasks.

Project Plan:
{plan}
  """
  return ARCHITECT_PROMPT