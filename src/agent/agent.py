from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from src.tools.sql_tools import execute_sql
from src.agent.prompts import AGENT_PROMPT 
from langgraph.checkpoint.memory import MemorySaver

def create_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    tools = [execute_sql]

    memory = MemorySaver()

    agent = create_react_agent(
        llm,
        tools,
        checkpointer=memory,
        prompt=AGENT_PROMPT,
    )

    return agent