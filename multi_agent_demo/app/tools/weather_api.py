# multi_agent_demo/app/tools/weather_api.py
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """获取某个城市的天气情况，适用于出行、活动等决策。"""
    return f"{city} 目前天气晴朗，气温 25°C，湿度 60%。"
