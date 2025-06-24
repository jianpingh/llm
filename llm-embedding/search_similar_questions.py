# -*- coding: utf-8 -*-
"""
基于 faiss 和 sentence-transformers 的相似问题检索工具
步骤说明：
1. 初始化时，输入问题列表，加载句向量模型，并将所有问题向量化。
2. 用 faiss 构建索引，将所有问题的向量加入索引。
3. 输入新问题时，先向量化，再用 faiss 检索最相似的问题。
"""
import faiss
from sentence_transformers import SentenceTransformer
from typing import List
import torch

class SimilarQuestionSearcher:
    def __init__(self, questions: List[str], model_name: str = 'distilbert-base-nli-stsb-mean-tokens', batch_size: int = 32, nlist: int = 100):
        """
        初始化相似问题检索器
        :param questions: 问题列表
        :param model_name: 句向量模型名称
        :param batch_size: 向量化批次大小
        :param nlist: IVF 聚类数（大数据量时使用）
        """
        self.questions = questions  # 保存原始问题
        self.model = SentenceTransformer(model_name)  # 使用轻量模型，默认使用 CPU
        with torch.no_grad():
            self.embeddings = self.model.encode(questions, batch_size=batch_size)  # 批量向量化
        self.dimension = self.embeddings.shape[1]  # 向量维度

        # 根据数据量选择索引类型
        if len(questions) >= nlist:
            # 大数据量时用 IndexIVFFlat
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(self.embeddings)
            self.index.add(self.embeddings)
        else:
            # 小数据量直接用 IndexFlatL2（无需训练）
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(self.embeddings)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """
        检索与输入问题最相似的问题
        :param query: 输入的问题
        :param top_k: 返回最相似的前k个问题
        :return: 相似问题列表
        """
        query_vec = self.model.encode([query])  # 输入问题向量化
        D, I = self.index.search(query_vec, top_k)  # faiss 检索
        return [self.questions[idx] for idx in I[0]]  # 返回相似问题

if __name__ == '__main__':
    print("test start：")
    # 示例问题列表，可替换为自己的问题库
    questions = [
        "什么是人工智能？",
        "如何使用Python进行数据分析？",
        "机器学习和深度学习的区别是什么？",
        "Python有哪些常用的数据分析库？",
        "什么是神经网络？"
    ]
    # 实例化检索器
    searcher = SimilarQuestionSearcher(questions)
    # 输入待检索问题
    query = input("请输入你的问题：")
    # 检索最相似的问题
    results = searcher.search(query)
    print("最相似的问题：")
    for q in results:
        print(q)
