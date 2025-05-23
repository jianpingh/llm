import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from tools import get_user_balance, transfer_funds, get_transaction_history, search_orders

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE")
)

tools = [
    get_user_balance,
    transfer_funds,
    get_transaction_history,
    search_orders
]

agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)
