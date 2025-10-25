from dotenv import load_dotenv
from langchain_groq import ChatGroq
from prompt import *
from states import *
from langgraph.constants import END
from langgraph.graph import StateGraph

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

user_prompt = "Create a simple calculator web application"

def planner_agent(state: dict) -> dict:
  users_prompt = planner_prompt(state["user_prompt"])
  resp = llm.with_structured_output(Plan).invoke(users_prompt)
  return {"plan": resp, END: True}

response = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))

print(response)

graph = StateGraph(dict)
graph.add_node("planner", planner_agent)