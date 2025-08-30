"""
索引管理模块
使用 LlamaIndex 构建和管理文档索引
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

logger = logging.getLogger(__name__)


class IndexManager:
    """索引管理器，负责创建、存储和检索文档索引"""
    
    def __init__(self, 
                 persist_dir: str = "./indexes/chroma_db",
                 collection_name: str = "research_documents",
                 openai_api_key: Optional[str] = None,
                 model_name: str = "gpt-4-turbo-preview",
                 embedding_model: str = "text-embedding-3-small",
                 top_k: int = 5,
                 similarity_threshold: float = 0.7):
        """
        初始化索引管理器
        
        Args:
            persist_dir: 持久化目录
            collection_name: 集合名称
            openai_api_key: OpenAI API密钥
            model_name: 使用的模型名称
            embedding_model: 嵌入模型名称
            top_k: 检索时返回的最相关文档数量
            similarity_threshold: 相似度阈值
        """
        self.persist_dir = Path(persist_dir)
        self.collection_name = collection_name
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        # 确保持久化目录存在
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置LlamaIndex设置
        self._setup_llama_index(model_name, embedding_model)
        
        # 初始化向量存储
        self.vector_store = self._setup_vector_store()
        self.index = None
        
        logger.info(f"索引管理器初始化完成，持久化目录: {persist_dir}")
    
    def _setup_llama_index(self, model_name: str, embedding_model: str):
        """配置LlamaIndex全局设置"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        try:
            # 禁用 LangChain 桥接以避免版本冲突
            import os
            os.environ["LLAMA_INDEX_DISABLE_LANGCHAIN_BRIDGE"] = "1"
            
            # 设置LLM
            Settings.llm = OpenAI(
                api_key=self.openai_api_key,
                model=model_name,
                temperature=0.1
            )
            
            # 设置嵌入模型 - 也设置到全局，确保一致性
            self.embed_model = OpenAIEmbedding(
                api_key=self.openai_api_key,
                model=embedding_model
            )
            Settings.embed_model = self.embed_model
            
            logger.info(f"LlamaIndex配置完成: LLM={model_name}, Embedding={embedding_model}")
        except Exception as e:
            logger.error(f"LlamaIndex配置失败: {str(e)}")
            raise
    
    def _setup_vector_store(self) -> ChromaVectorStore:
        """设置ChromaDB向量存储"""
        try:
            # 创建ChromaDB客户端
            chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
            
            # 获取或创建集合
            chroma_collection = chroma_client.get_or_create_collection(
                name=self.collection_name
            )
            
            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            
            logger.info(f"ChromaDB向量存储初始化完成，集合: {self.collection_name}")
            return vector_store
            
        except Exception as e:
            logger.error(f"设置向量存储失败: {str(e)}")
            raise
    
    def create_index(self, documents: List[Document], force_rebuild: bool = False) -> VectorStoreIndex:
        """
        创建或加载文档索引
        
        Args:
            documents: 文档列表
            force_rebuild: 是否强制重建索引
            
        Returns:
            向量索引对象
        """
        try:
            # 检查是否已有索引且不强制重建
            if not force_rebuild and self._index_exists():
                logger.info("加载现有索引...")
                self.index = self._load_existing_index()
            else:
                logger.info("创建新索引...")
                self.index = self._build_new_index(documents)
            
            logger.info("索引创建/加载完成")
            return self.index
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise
    
    def _index_exists(self) -> bool:
        """检查索引是否已存在"""
        try:
            collection = self.vector_store.chroma_collection
            return collection.count() > 0
        except Exception:
            return False
    
    def _load_existing_index(self) -> VectorStoreIndex:
        """加载现有索引"""
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        return VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=storage_context
        )
    
    def _build_new_index(self, documents: List[Document]) -> VectorStoreIndex:
        """构建新索引"""
        if not documents:
            raise ValueError("文档列表不能为空")
        
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # 创建索引（使用全局设置中的嵌入模型）
        index = VectorStoreIndex.from_documents(
            documents=documents,
            storage_context=storage_context,
            show_progress=True
        )
        
        logger.info(f"新索引构建完成，包含 {len(documents)} 个文档")
        return index
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        向现有索引添加文档
        
        Args:
            documents: 要添加的文档列表
        """
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")
        
        try:
            for doc in documents:
                self.index.insert(doc)
            
            logger.info(f"成功添加 {len(documents)} 个文档到索引")
            
        except Exception as e:
            logger.error(f"添加文档到索引失败: {str(e)}")
            raise
    
    def get_retriever(self, similarity_top_k: int = None, **kwargs):
        """
        获取检索器
        
        Args:
            similarity_top_k: 返回最相似的文档数量，如果不指定则使用配置的默认值
            **kwargs: 其他检索器参数
            
        Returns:
            检索器对象
        """
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")
        
        # 使用配置的默认值
        if similarity_top_k is None:
            similarity_top_k = self.top_k
        
        return self.index.as_retriever(
            similarity_top_k=similarity_top_k,
            **kwargs
        )
    
    def get_query_engine(self, **kwargs):
        """
        获取查询引擎
        
        Args:
            **kwargs: 查询引擎参数
            
        Returns:
            查询引擎对象
        """
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")
        
        return self.index.as_query_engine(**kwargs)
    
    def search_similar(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回数量，如果不指定则使用配置的默认值
            
        Returns:
            相似文档列表
        """
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")

        # 使用配置的默认值
        if top_k is None:
            top_k = self.top_k

        try:
            retriever = self.get_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query)
            
            results = []
            for node in nodes:
                results.append({
                    "text": node.text,
                    "score": node.score,
                    "metadata": node.metadata
                })
            
            logger.info(f"搜索完成，返回 {len(results)} 个相似文档")
            return results
            
        except Exception as e:
            logger.error(f"搜索相似文档失败: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        获取索引统计信息
        
        Returns:
            索引统计信息
        """
        if not self.index:
            return {"status": "未初始化"}
        
        try:
            collection = self.vector_store.chroma_collection
            doc_count = collection.count()
            
            return {
                "status": "已初始化",
                "document_count": doc_count,
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_dir)
            }
            
        except Exception as e:
            logger.error(f"获取索引统计失败: {str(e)}")
            return {"status": "错误", "error": str(e)}
    
    def clear_index(self) -> None:
        """清空索引"""
        try:
            # 删除集合
            chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
            chroma_client.delete_collection(name=self.collection_name)
            
            # 重新初始化
            self.vector_store = self._setup_vector_store()
            self.index = None
            
            logger.info("索引已清空")
            
        except Exception as e:
            logger.error(f"清空索引失败: {str(e)}")
            raise
