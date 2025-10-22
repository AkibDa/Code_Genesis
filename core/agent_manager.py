import yaml
from core.model_router import ModelRouter

class AgentManager:
    def __init__(self, config_path="config/agents.yaml"):
        with open(config_path, "r") as f:
            self.agents = yaml.safe_load(f)["agents"]
        self.router = ModelRouter()

    def run_agent(self, agent_name, prompt):
        agent = self.agents[agent_name]
        primary = agent["primary_model"]
        backup = agent["backup_model"]

        response = self.router.query_model(primary, prompt)
        if "error" in str(response).lower():
            print(f"⚠️ Primary model failed for {agent_name}, switching to backup...")
            response = self.router.query_model(backup, prompt)
        return response
