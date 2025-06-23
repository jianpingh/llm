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
    agent = CustomerAgent(retriever, None, None)

    mock_response = {
        "choices": [
            {"text": "这是一个测试回答。"}
        ]
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = lambda: None

        result = agent.query_open_api("测试问题")
        assert result == "这是一个测试回答。"
