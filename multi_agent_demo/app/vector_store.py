# multi_agent_demo/app/vector_store.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from app.config import CHROMA_PATH, DATA_DIR

def load_index():
    # 1. 读取文档
    docs = SimpleDirectoryReader(DATA_DIR).load_data()
    # 2. 初始化本地 Chroma client & collection
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("handbook")
    # 3. 用 collection 创建向量存储
    vector_store = ChromaVectorStore(chroma_collection=collection)
    # 4. 构建存储上下文（并指定 persist_dir，可选）
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # 5. 创建索引
    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=OpenAIEmbedding(),
    )
    return index
