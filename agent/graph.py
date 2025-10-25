from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")

response = llm.invoke("Write a poem about the sea.")

print(response.content)