# 电商客服 Agent 核心代码

# 此文件包含电商客服的主要逻辑实现

import requests
import os
from dotenv import load_dotenv

load_dotenv()

class CustomerAgent:
    def __init__(self, faq_retriever, product_api, order_api):
        self.faq_retriever = faq_retriever
        self.product_api = product_api
        self.order_api = order_api
        self.api_key = os.getenv("API_KEY")

    def handle_query(self, query):
        if "FAQ" in query:
            return self.faq_retriever.retrieve(query)
        elif "商品" in query:
            product_info = self.product_api.get_product_info(query)
            llm_response = self.query_open_api(f"关于商品的信息: {product_info}")
            return llm_response
        elif "订单" in query:
            order_status = self.order_api.get_order_status(query)
            llm_response = self.query_open_api(f"关于订单的信息: {order_status}")
            return llm_response
        else:
            return "无法处理该请求，请提供��多信息。"

    def query_open_api(self, query):
        try:
            response = requests.post(
                os.getenv("API_URL"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "text-davinci-003",
                    "prompt": query,
                    "max_tokens": 100
                }
            )
            response.raise_for_status()
            return response.json().get("choices", [{}])[0].get("text", "无法获取回答。")
        except requests.exceptions.RequestException as e:
            return f"请求失败: {e}"
