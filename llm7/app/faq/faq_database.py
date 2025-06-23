# FAQ 数据库或数据源

# 此文件包含 FAQ 数据库的相关操作

class FAQDatabase:
    def __init__(self):
        self.data = {
            "退货": "退货政策为7天无理由退货。",
            "发货": "发货时间通常为1-3个工作日。"
        }

    def search(self, query):
        return self.data.get(query, "未找到相关FAQ。")
