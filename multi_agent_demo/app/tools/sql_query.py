# multi_agent_demo/app/tools/sql_query.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 定义参数 schema，包含 production_id 和 product_name
class SalesQueryArgs(BaseModel):
    production_id: str = Field(..., description="后端系统中对应产品的 productionId")
    product_name: str = Field(..., description="要查询销量的产品名称")

@tool(
    "query_sales",
    description=(
        "查询数据库中某个产品的上个月销量信息，"
        "需要 productionId（后端产品ID）和 product_name，返回字符串结果。"
    ),
    args_schema=SalesQueryArgs
)
def query_sales(production_id: str, product_name: str) -> str:
    """
    查询数据库中某个产品的销量信息。

    参数:
      - production_id: 后端系统中产品的唯一 ID
      - product_name: 产品名称，用于结果展示

    返回:
      字符串形式的销量报告，
      例如“Product-123 上个月销量为 1345 件，排名第 2。”
    """
    # —— 在这里写实际的 HTTP 请求或数据库查询逻辑 ——
    # 例如调用你的后端 service：
    # resp = http.get(f"https://api.yourdomain.com/sales", params={
    #     "productionId": production_id,
    #     "name": product_name
    # })
    # data = resp.json()
    # return f"{product_name}（ID={production_id}）上个月销量为 {data['count']} 件，排名第 {data['rank']}。"

    # 演示返回
    return f"{product_name}（ID={production_id}）上个月销量为 1345 件，排名第 2。"
