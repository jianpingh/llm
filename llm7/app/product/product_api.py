# 商品 API 调用代码

# 此文件包含商品相关的 API 调用逻辑

class ProductAPI:
    def get_product_info(self, product_id):
        # 模拟调用外部API获取商品信息
        return {
            "id": product_id,
            "name": "示例商品",
            "price": 299.99
        }
