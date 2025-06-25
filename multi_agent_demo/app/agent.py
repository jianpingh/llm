# multi_agent_demo/app/agent.py

from langchain.chat_models.openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from app.tools.doc_qa import ask_docs
from app.tools.weather_api import get_weather
from app.tools.sql_query import query_sales
from app.config import OPENAI_API_KEY, OPENAI_API_BASE

def get_multi_tool_agent():
    tools = [ask_docs, get_weather, query_sales]

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
        openai_api_base=OPENAI_API_BASE
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True
    )
    return agent
