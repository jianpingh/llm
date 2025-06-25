# multi_agent_demo/app/tools/weather_api.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 定义参数 schema，包含 city
class WeatherQueryArgs(BaseModel):
    city: str = Field(..., description="要查询天气的城市名称")

@tool(
    "get_weather",
    description="获取某个城市的天气情况，适用于出行、活动等决策，需要 city 参数，返回字符串结果。",
    args_schema=WeatherQueryArgs
)
def get_weather(city: str) -> str:
    """
    获取某个城市的天气情况。

    参数:
      - city: 城市名称

    返回:
      字符串形式的天气报告，
      例如“北京 目前天气晴朗，气温 25°C，湿度 60%。”
    """
    # —— 在这里写实际的 HTTP 请求或第三方天气 API 查询逻辑 ——
    # 例如：
    # resp = http.get(f"https://api.weather.com/v1/weather", params={"city": city})
    # data = resp.json()
    # return f"{city} 目前天气{data['desc']}，气温 {data['temp']}°C，湿度 {data['humidity']}%。"

    # 演示返回
    return f"{city} 目前天气晴朗，气温 25°C，湿度 60%。"
