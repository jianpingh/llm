import chromadb
from sentence_transformers import SentenceTransformer

# 初始化 Chroma 客户端
client = chromadb.Client()

# 创建一个新的集合
collection_name = "example_collection"
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
query_embedding = model.encode([query])
print("query_embedding 向量：", query_embedding)

# 在 Chroma 中查询与查询文本最相似的文本
results = collection.query(
    query_embeddings=query_embedding,  
    n_results=1
)

# 显示查询结果
for doc, dist in zip(results['documents'], results['distances']):
    print(f"Document: {doc}, Similarity: {dist}")
