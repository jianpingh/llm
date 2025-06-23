# 商品模块的测试

# 此文件包含商品模块的单元测试

import pytest
from app.product.product_database import ProductDatabase
from app.product.product_api import ProductAPI

def test_product_database():
    database = ProductDatabase()

    assert database.get_product("001") == {"name": "商品A", "price": 50}
    assert database.get_product("002") == {"name": "商品B", "price": 100}
    assert database.get_product("003") == "未找到商品信息。"

def test_product_api():
    api = ProductAPI()

    product_info = api.get_product_info("001")
    assert product_info["id"] == "001"
    assert product_info["name"] == "示例商品"
    assert product_info["price"] == 100.0
