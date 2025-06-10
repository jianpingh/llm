# multi_agent_demo/app/vector_store.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
from app.config import CHROMA_PATH, DATA_DIR

def load_index():
    docs = SimpleDirectoryReader(DATA_DIR).load_data()
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection("handbook")

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        docs,
        storage_context=storage_context,
        embed_model=OpenAIEmbedding()
    )
    return index

