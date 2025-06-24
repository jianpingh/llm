import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

class ChromaLocalDB:
    def __init__(self, db_path='chroma_db'):
        self.db_path = db_path
        self.index_path = os.path.join(db_path, 'faiss.index')
        self.meta_path = os.path.join(db_path, 'meta.pkl')
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.texts = []
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, 'rb') as f:
                self.texts = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(384)  # 384为all-MiniLM-L6-v2输出维度

    def add(self, texts):
        embeddings = self.model.encode(texts)
        self.index.add(embeddings)
        self.texts.extend(texts)
        self._save()

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'wb') as f:
            pickle.dump(self.texts, f)

    def search(self, query, top_k=5):
        embedding = self.model.encode([query])
        D, I = self.index.search(embedding, top_k)
        return [(self.texts[i], float(D[0][idx])) for idx, i in enumerate(I[0])]

if __name__ == '__main__':
    db = ChromaLocalDB()
    # 读取faq.txt内容
    faq_path = 'faq.txt'
    if os.path.exists(faq_path):
        with open(faq_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
        # 合并Q/A为一条，忽略空行
        qa_pairs = []
        q, a = '', ''
        for line in lines:
            if line.startswith('Q:'):
                q = line.strip()
            elif line.startswith('A:'):
                a = line.strip()
            if q and a:
                qa_pairs.append(f"{q}\n{a}")
                q, a = '', ''
        if qa_pairs:
            db.add(qa_pairs)
    else:
        print('未找到faq.txt')

    print('当前数据库所有问答：')
    for idx, qa in enumerate(db.texts):
        print(f'{idx+1}. {qa}')

    print('请输入您的问题（输入exit退出）：')
    while True:
        user_input = input('> ').strip()
        if user_input.lower() == 'exit':
            break
        results = db.search(user_input, top_k=1)
        if results:
            print('最相似的问答：')
            print(results[0][0])
        else:
            print('未找到相似问答。')
