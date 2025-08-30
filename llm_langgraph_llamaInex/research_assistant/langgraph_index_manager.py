"""
LangGraph + LlamaIndex 集成的索引管理模块
使用兼容版本避免冲突
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

# LlamaIndex 导入
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.core import Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.storage_context import StorageContext

logger = logging.getLogger(__name__)


class LangGraphIndexManager:
    """兼容 LangGraph 的索引管理器"""
    
    def __init__(self, 
                 persist_dir: str = "./indexes/langgraph_db",
                 openai_api_key: Optional[str] = None,
                 model_name: str = "gpt-3.5-turbo",
                 embedding_model: str = "text-embedding-ada-002",
                 top_k: int = 5,
                 similarity_threshold: float = 0.7):
        """初始化索引管理器"""
        self.persist_dir = Path(persist_dir)
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        # 确保目录存在
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置服务上下文
        self.service_context = self._create_service_context(model_name, embedding_model)
        
        # 初始化
        self.documents = []
        self.index = None
        
        logger.info(f"LangGraph 索引管理器初始化完成")
    
    def _create_service_context(self, model_name: str, embedding_model: str) -> ServiceContext:
        """创建服务上下文"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        try:
            # 创建 LLM
            llm = OpenAI(
                api_key=self.openai_api_key,
                model=model_name,
                temperature=0.1
            )
            
            # 创建嵌入模型
            embed_model = OpenAIEmbedding(
                api_key=self.openai_api_key,
                model=embedding_model
            )
            
            # 创建服务上下文
            service_context = ServiceContext.from_defaults(
                llm=llm,
                embed_model=embed_model
            )
            
            logger.info(f"服务上下文配置完成: LLM={model_name}, Embedding={embedding_model}")
            return service_context
            
        except Exception as e:
            logger.error(f"服务上下文配置失败: {str(e)}")
            raise
    
    def create_index(self, documents: List[Document], force_rebuild: bool = False) -> VectorStoreIndex:
        """创建索引"""
        try:
            if not documents:
                logger.warning("没有文档可以索引")
                return None
            
            logger.info("创建向量索引...")
            
            # 创建存储上下文
            vector_store = SimpleVectorStore()
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 创建索引
            self.index = VectorStoreIndex.from_documents(
                documents=documents,
                service_context=self.service_context,
                storage_context=storage_context,
                show_progress=True
            )
            
            # 可选：持久化索引
            if self.persist_dir:
                try:
                    self.index.storage_context.persist(persist_dir=str(self.persist_dir))
                    logger.info(f"索引已持久化到: {self.persist_dir}")
                except Exception as e:
                    logger.warning(f"索引持久化失败: {str(e)}")
            
            self.documents = documents
            logger.info(f"索引创建完成，包含 {len(documents)} 个文档")
            return self.index
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise
    
    def load_index(self) -> VectorStoreIndex:
        """加载现有索引"""
        try:
            if self.persist_dir.exists() and any(self.persist_dir.iterdir()):
                logger.info("加载现有索引...")
                storage_context = StorageContext.from_defaults(persist_dir=str(self.persist_dir))
                self.index = VectorStoreIndex.from_storage(
                    storage_context=storage_context,
                    service_context=self.service_context
                )
                logger.info("索引加载完成")
                return self.index
            else:
                logger.info("没有找到现有索引")
                return None
        except Exception as e:
            logger.error(f"加载索引失败: {str(e)}")
            return None
    
    def get_retriever(self, similarity_top_k: int = None, **kwargs):
        """获取检索器"""
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")
        
        if similarity_top_k is None:
            similarity_top_k = self.top_k
        
        return self.index.as_retriever(
            similarity_top_k=similarity_top_k,
            **kwargs
        )
    
    def get_query_engine(self, **kwargs):
        """获取查询引擎"""
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")
        
        return self.index.as_query_engine(
            service_context=self.service_context,
            **kwargs
        )
    
    def search_similar(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        if not self.index:
            raise ValueError("索引未初始化，请先创建索引")

        if top_k is None:
            top_k = self.top_k

        try:
            retriever = self.get_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query)
            
            results = []
            for node in nodes:
                results.append({
                    'content': node.node.text if hasattr(node, 'node') else node.text,
                    'score': node.score if hasattr(node, 'score') else 0.0,
                    'metadata': node.node.metadata if hasattr(node, 'node') else getattr(node, 'metadata', {})
                })
            
            logger.debug(f"检索到 {len(results)} 个相关文档")
            return results
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def add_documents(self, documents: List[Document]):
        """添加文档"""
        if not self.index:
            return self.create_index(documents)
        
        try:
            all_documents = self.documents + documents
            return self.create_index(all_documents, force_rebuild=True)
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计信息"""
        if not self.index:
            return {"status": "未初始化"}
        
        return {
            "status": "已初始化",
            "document_count": len(self.documents),
            "index_type": "VectorStoreIndex (LangGraph Compatible)",
            "persist_dir": str(self.persist_dir)
        }
