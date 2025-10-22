import yaml
from core.agent_manager import AgentManager

class TaskManager:
  def __init__(self, config_path="config/tasks.yaml"):
    with open(config_path, "r") as f:
      self.tasks = yaml.safe_load(f)["tasks"]
    self.agent_manager = AgentManager()
    self.context = {}

  def execute_task(self, task_name):
    task = self.tasks[task_name]
    agent_name = task["agent"]
    deps = task.get("dependencies", [])

    # Pass previous outputs as context
    context_data = {dep: self.context.get(dep) for dep in deps}
    prompt = f"Task: {task_name}\nContext: {context_data}\nDescription: {task['description']}"
    
    response = self.agent_manager.run_agent(agent_name, prompt)
    self.context[task_name] = response
    print(f"✅ {task_name} completed by {agent_name}")
    return response

  def execute_all(self):
    for task_name in self.tasks:
      self.execute_task(task_name)
    return self.context
