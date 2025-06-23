# 商品信息数据库

# 此文件包含商品信息数据库的相关操作

class ProductDatabase:
    def __init__(self):
        self.products = {
            "001": {"name": "商品A", "price": 50},
            "002": {"name": "商品B", "price": 100}
        }

    def get_product(self, product_id):
        return self.products.get(product_id, "未找到商品信息。")
