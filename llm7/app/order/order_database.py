# 订单信息数据库

# 此文件包含订单信息数据库的相关操作


class OrderDatabase:
    def __init__(self):
        self.orders = {
            "1001": {"status": "已发货"},
            "1002": {"status": "待发货"}
        }

    def get_order(self, order_id):
        return self.orders.get(order_id, "未找到订单信息。")
