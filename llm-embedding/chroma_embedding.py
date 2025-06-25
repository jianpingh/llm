import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

# 初始化 Chroma 客户端
client = chromadb.Client()

# 创建一个新的集合
collection_name = "example_collection"
# 如果集合已存在，可先删除或获取
try:
    client.delete_collection(collection_name)
except:
    pass
collection = client.create_collection(collection_name)

# 加载 SentenceTransformer 模型
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 输入文本（示例问题）
texts = [
    "What is machine learning?",
    "How does neural network work?",
    "Explain the difference between machine learning and deep learning.",
    "What is artificial intelligence?"
]

# 将文本转化为向量
embeddings = model.encode(texts)

# 打印嵌入向量的详细信息
print("📝 文本嵌入向量详情：")
for idx, (text, emb) in enumerate(zip(texts, embeddings)):
    emb = np.array(emb)
    print(f"ID: {idx}")
    print(f"文本: {text}")
    print(f"向量维度: {emb.shape[0]}")
    print(f"向量值（前5维）: {emb[:5].tolist()}")
    print(f"向量值（后5维）: {emb[-5:].tolist()}")
    print(f"最小值: {float(emb.min()):.6f}, 最大值: {float(emb.max()):.6f}, 均值: {float(emb.mean()):.6f}")
    print("-" * 60)

# 向集合中添加数据
collection.add(
    documents=texts,
    embeddings=embeddings,
    metadatas=[{"source": text} for text in texts],
    ids=[str(i) for i in range(len(texts))]
)

# 新的问题或查询文本
query = "What is AI?"

# 将查询文本转化为向量
query_embedding = model.encode([query])[0]
print("\n📝 查询嵌入向量详情：")
qe = np.array(query_embedding)
print(f"查询: {query}")
print(f"维度: {qe.shape[0]}")
print(f"前5维: {qe[:5].tolist()}")
print(f"后5维: {qe[-5:].tolist()}")
print(f"最小值: {float(qe.min()):.6f}, 最大值: {float(qe.max()):.6f}, 均值: {float(qe.mean()):.6f}")
print("-" * 60)

# 在 Chroma 中查询与查询文本最相似的文本
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)

# 显示查询结果
print("\n🔍 查询结果：")
for doc, dist in zip(results['documents'][0], results['distances'][0]):
    print(f"Document: {doc}")
    print(f"Similarity score (距离): {dist:.6f}")
