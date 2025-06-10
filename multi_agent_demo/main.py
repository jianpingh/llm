# multi_agent_demo/main.py
from dotenv import load_dotenv
load_dotenv()

from app.agent import get_multi_tool_agent

if __name__ == "__main__":
    agent = get_multi_tool_agent()
    while True:
        question = input("\n👤 你想问什么？> ")
        if question.lower() in ["exit", "quit"]:
            break
        answer = agent.run(question)
        print("🤖 Agent 回答：", answer)
