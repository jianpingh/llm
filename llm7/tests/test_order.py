# 订单模块的测试

# 此文件包含订单模块的单元测试

import pytest
from app.order.order_database import OrderDatabase
from app.order.order_api import OrderAPI

def test_order_database():
    database = OrderDatabase()

    assert database.get_order("1001") == {"status": "已发货"}
    assert database.get_order("1002") == {"status": "待发货"}
    assert database.get_order("1003") == "未找到订单信息。"

def test_order_api():
    api = OrderAPI()

    order_status = api.get_order_status("1001")
    assert order_status["order_id"] == "1001"
    assert order_status["status"] == "已发货"
