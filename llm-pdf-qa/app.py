# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.openai import OpenAIEmbedding as BaseOpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import openai

# 0. 清理代理环境变量，必须在任何 openai 导入之前
for var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    os.environ.pop(var, None)

# 1. 加载 .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
if not API_KEY:
    raise ValueError("❌ 请在 .env 中设置 OPENAI_API_KEY")

openai.api_key = API_KEY
openai.api_base = API_BASE

# 2. 自定义去除 proxies 参数的嵌入类
class OpenAIEmbeddingNoProxy(BaseOpenAIEmbedding):
    def _get_client(self):
        kw = self._get_credential_kwargs()
        kw.pop("proxies", None)
        from openai import OpenAI
        return OpenAI(**kw)

# 3. 初始化嵌入模型
embed_model = OpenAIEmbeddingNoProxy(
    model_name="text-embedding-ada-002",
    openai_api_key=API_KEY,
    openai_api_base=API_BASE,
)

# 4. 配置本地持久化路径和集合名
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "doc_collection"

# 5. 初始化 Chroma 本地客户端并获取（或创建）集合
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

# 6. 创建向量存储
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 7. 创建 StorageContext，并在此时指定 persist_dir
storage_context = StorageContext.from_defaults(
    vector_store=vector_store,
    persist_dir=PERSIST_DIR,
)

# 8. 尝试加载已有索引，若不存在则构建并持久化
try:
    index = load_index_from_storage(storage_context)
    print("✅ 已加载本地向量索引")
except ValueError:
    print("🔄 未检测到已有索引，正在构建新的向量索引...")
    documents = SimpleDirectoryReader("./docs").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    storage_context.persist()
    print(f"✅ 向量索引已构建并保存到 {PERSIST_DIR}")

# # --- 打印向量库中所有数据的详细信息 ---
# print("\n📊 当前向量库数据详情：")
# data = chroma_collection.get(include=["documents", "metadatas", "embeddings"])
# for doc, meta, emb in zip(data["documents"], data["metadatas"], data["embeddings"]):
#     print(f"文档内容: {doc}")
#     print(f"元数据: {meta}")
#     print(f"向量长度: {len(emb)}, 前5维: {emb[:5]}")
#     print("-" * 40)

# 9. 创建查询引擎并启动交互循环（中文回答）
query_engine = index.as_query_engine(response_mode="compact")
print("\n📚 文档问答系统已启动，输入 exit 退出")
while True:
    q = input("\n❓ 请输入你的问题：").strip()
    if q.lower() in ("exit", "quit", "退出"):
        print("👋 再见！")
        break
    ans = query_engine.query(f"请用中文回答：{q}")
    print(f"\n💡 回答（中文）：\n{ans.response}\n")
