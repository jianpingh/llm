# multi_agent_demo/app/tools/doc_qa.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.vector_store import load_index

index = load_index()
query_engine = index.as_query_engine()

# 定义参数 schema，包含 question
class DocQAQueryArgs(BaseModel):
    question: str = Field(..., description="要查询的文档问题")

@tool(
    "ask_docs",
    description="从上传的公司文档中获取知识，例如手册、规定、产品说明等，需要 question 参数，返回字符串结果。",
    args_schema=DocQAQueryArgs
)
def ask_docs(question: str) -> str:
    """
    从上传的公司文档中获取知识。

    参数:
      - question: 要查询的文档问题

    返回:
      字符串形式的文档问答结果。
    """
    return str(query_engine.query(question))
