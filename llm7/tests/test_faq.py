# FAQ 模块的测试

# 此文件包含 FAQ 模块的单元测试

import pytest
from app.customer_agent import CustomerAgent
from app.faq.faq_database import FAQDatabase
from app.faq.faq_retriever import FAQRetriever
import requests
from unittest.mock import patch

def test_faq_retrieval():
    database = FAQDatabase()
    retriever = FAQRetriever(database)

    assert retriever.retrieve("退货") == "退货政策为7天无理由退货。"
    assert retriever.retrieve("发货") == "发货时间通常为1-3个工作日。"
    assert retriever.retrieve("未知") == "未找到相关FAQ。"

def test_open_api_query():
    database = FAQDatabase()
    retriever = FAQRetriever(database)
    # 导入商品和订单API
    from app.product.product_api import ProductAPI
    from app.order.order_api import OrderAPI
    product_api = ProductAPI()
    order_api = OrderAPI()
    agent = CustomerAgent(retriever, product_api, order_api)

    result = agent.handle_query("FAQ:退货")
    print("FAQ测试结果:", result)

    result = agent.handle_query("商品:手机")
    print("商品测试结果:", result)

    result = agent.handle_query("订单:12345")
    print("订单测试结果:", result)
