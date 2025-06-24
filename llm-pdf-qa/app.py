# 导入必要的模块
# VectorStoreIndex 用于构建向量索引
# SimpleDirectoryReader 用于读取本地文档
# OpenAIEmbedding 用于嵌入模型
import os
from dotenv import load_dotenv
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取 API 密钥和代理地址
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

# 检查 API 密钥是否有效
if not openai.api_key:
    raise ValueError("API 密钥未设置！请检查 .env 文件或环境变量。")

# 加载本地文档，路径为 ./docs
documents = SimpleDirectoryReader("./docs").load_data()

# 初始化嵌入模型，使用 OpenAI 的 text-embedding-ada-002 模型
embed_model = OpenAIEmbedding(
    model_name="text-embedding-ada-002"
)

# 构建向量索引
index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

# 初始化查询引擎
query_engine = index.as_query_engine()

# 执行查询并打印结果
response = query_engine.query("文档的核心观点是什么？")
print(response)
