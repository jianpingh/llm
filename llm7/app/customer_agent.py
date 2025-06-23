# 电商客服 Agent 核心代码

# 此文件包含电商客服的主要逻辑实现

class CustomerAgent:
    def __init__(self, faq_retriever, product_api, order_api):
        self.faq_retriever = faq_retriever
        self.product_api = product_api
        self.order_api = order_api

    def handle_query(self, query):
        if "FAQ" in query:
            return self.faq_retriever.retrieve(query)
        elif "商品" in query:
            return self.product_api.get_product_info(query)
        elif "订单" in query:
            return self.order_api.get_order_status(query)
        else:
            return "无法处理该请求，请提供更多信息。"
