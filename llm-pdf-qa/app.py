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

# 0. 清理系统代理变量，防止意外挂载 proxies
for proxy in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    os.environ.pop(proxy, None)

# 1. 加载 .env
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
if not API_KEY:
    raise ValueError("❌ 请在 .env 中设置 OPENAI_API_KEY")

openai.api_key = API_KEY
openai.api_base = API_BASE

# 2. 去除 proxies 的 OpenAIEmbedding 子类
class OpenAIEmbeddingNoProxy(BaseOpenAIEmbedding):
    def _get_client(self):
        kw = self._get_credential_kwargs()
        kw.pop("proxies", None)
        from openai import OpenAI
        return OpenAI(**kw)

embed_model = OpenAIEmbeddingNoProxy(
    model_name="text-embedding-ada-002",
    openai_api_key=API_KEY,
    openai_api_base=API_BASE,
)

# 3. Chroma 本地持久化设置
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "doc_collection"

# 4. 初始化本地 Chroma 客户端并获取 Collection
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

# 5. 正确传入 chroma_collection 关键字参数
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# 6. 构建存储上下文
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 7. 尝试加载已有索引，失败则重建并持久化
try:
    index = load_index_from_storage(storage_context)
    print("✅ 已加载本地向量索引")
except ValueError:
    print("🔄 未检测到索引，正在构建新的向量索引...")
    documents = SimpleDirectoryReader("./docs").load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    index.storage_context.persist(PERSIST_DIR)
    print("✅ 向量索引已构建并保存")

# 8. 创建查询引擎并进入交互循环
query_engine = index.as_query_engine()
print("\n📚 文档问答系统已启动，输入 exit 退出")
while True:
    q = input("\n❓ 请输入你的问题：").strip()
    if q.lower() in ("exit", "quit", "退出"):
        print("👋 再见！")
        break
    answer = query_engine.query(q)
    print(f"\n💡 回答：\n{answer}\n")
