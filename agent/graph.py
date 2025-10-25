from dotenv import load_dotenv
from langchain_groq import ChatGroq
from prompt import *
from states import *

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

user_prompt = "Create a simple calculator web application"

prompt = planner_prompt(user_prompt)

response = llm.with_structured_output(Plan).invoke(prompt)

print(response)