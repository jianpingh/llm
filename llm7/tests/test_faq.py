# FAQ 模块的测试

# 此文件包含 FAQ 模块的单元测试

import pytest
from app.faq.faq_database import FAQDatabase
from app.faq.faq_retriever import FAQRetriever

def test_faq_retrieval():
    database = FAQDatabase()
    retriever = FAQRetriever(database)

    assert retriever.retrieve("退货") == "退货政策为7天无理由退货。"
    assert retriever.retrieve("发货") == "发货时间通常为1-3个工作日。"
    assert retriever.retrieve("未知") == "未找到相关FAQ。"
