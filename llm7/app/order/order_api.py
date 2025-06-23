# 订单 API 调用代码

# 此文件包含订单相关的 API 调用逻辑

class OrderAPI:
    def get_order_status(self, order_id):
        # 模拟调用外部API获取订单状态
        return {
            "order_id": order_id,
            "status": "已发货"
        }
