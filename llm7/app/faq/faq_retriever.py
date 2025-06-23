# FAQ 检索模块

# 此文件包含 FAQ 检索的主要逻辑实现

class FAQRetriever:
    def __init__(self, database):
        self.database = database

    def retrieve(self, query):
        return self.database.search(query)
