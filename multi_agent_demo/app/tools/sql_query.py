# multi_agent_demo/app/tools/sql_query.py
from langchain_core.tools import tool

@tool
def query_sales(product_name: str) -> str:
    """查询数据库中某个产品的销量信息。"""
    return f"{product_name} 上个月销量为 1345 件，排名第 2。"
