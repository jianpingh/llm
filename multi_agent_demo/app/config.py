# multi_agent_demo/app/config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", None)  # 支持代理地址
CHROMA_PATH = "./chroma_db"
DATA_DIR = "./data"
