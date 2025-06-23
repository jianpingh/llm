# 电商客服 Agent 核心代码

# 此文件包含电商客服的主要逻辑实现

import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class CustomerAgent:
    def __init__(self, faq_retriever, product_api, order_api):
        self.faq_retriever = faq_retriever
        self.product_api = product_api
        self.order_api = order_api
        self.api_key = os.getenv("API_KEY")
        self.api_proxy_url = os.getenv("API_PROXY_URL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_proxy_url
        )

    def infer_intent(self, query):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一个意图识别助手，只需回答：FAQ查询、商品查询或订单查询。"},
                    {"role": "user", "content": f"{query}"}
                ],
                max_tokens=50
            )
            intent = response.choices[0].message.content.strip()
            return intent
        except Exception as e:
            return f"请求失败: {e}"

    def query_open_api(self, query):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是一个电商智能客服，请根据用户提供的信息进行总结和专业回复。"},
                    {"role": "user", "content": query}
                ],
                max_tokens=200
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"请求失败: {e}"

    def handle_query(self, query):
        intent = self.infer_intent(query)
        if "FAQ" in intent:
            faq_answer = self.faq_retriever.retrieve(query)
            return self.query_open_api(f"用户问题：{query}\nFAQ知识库回答：{faq_answer}\n请用专业客服语气总结回复用户。")
        elif "商品" in intent:
            product_info = self.product_api.get_product_info(query)
            return self.query_open_api(f"用户问题：{query}\n商品信息：{product_info}\n请用专业客服语气总结回复用户。")
        elif "订单" in intent:
            order_status = self.order_api.get_order_status(query)
            return self.query_open_api(f"用户问题：{query}\n订单信息：{order_status}\n请用专业客服语气总结回复用户。")
        else:
            return "无法处理该请求，请提供更多信息。"
