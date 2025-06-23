# FAQ 数据库或数据源

# 此文件包含 FAQ 数据库的相关操作

class FAQDatabase:
    def __init__(self):
        self.data = {}
        self._load_data()

    def _load_data(self):
        try:
            with open(r"app/faq.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if '？' in line:
                        q, a = line.split('？', 1)
                        question = q.strip() + '？'
                        answer = a.strip()
                        self.data[question] = answer
        except Exception as e:
            print(f"加载faq.txt失败: {e}")

    def search(self, query):
        return self.data.get(query, "未找到相关FAQ。")
