# multi_agent_demo/app/tools/doc_qa.py
from langchain_core.tools import tool
from app.vector_store import load_index

index = load_index()
query_engine = index.as_query_engine()

@tool
def ask_docs(question: str) -> str:
    """从上传的公司文档中获取知识，例如手册、规定、产品说明等。"""
    return str(query_engine.query(question))
