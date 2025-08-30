"""
最小化的索引管理模块
完全避免 LangChain 相关的导入
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

# 只导入必要的 LlamaIndex 核心组件
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core import Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

logger = logging.getLogger(__name__)


class MinimalIndexManager:
    """最小化的索引管理器，完全避免版本冲突"""
    
    def __init__(self, 
                 persist_dir: str = "./indexes/simple_db",
                 openai_api_key: Optional[str] = None,
                 model_name: str = "gpt-3.5-turbo",
                 embedding_model: str = "text-embedding-ada-002",
                 top_k: int = 5,
                 similarity_threshold: float = 0.7):
        """初始化最小化索引管理器"""
        self.persist_dir = Path(persist_dir)
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        # 确保目录存在
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置 LlamaIndex
        self._setup_llama_index(model_name, embedding_model)
        
        # 初始化
        self.documents = []
        self.index = None
        
        logger.info(f"最小化索引管理器初始化完成")
    
    def _setup_llama_index(self, model_name: str, embedding_model: str):
        """配置LlamaIndex全局设置"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        try:
            # 设置LLM
            Settings.llm = OpenAI(
                api_key=self.openai_api_key,
                model=model_name,
                temperature=0.1
            )
            
            # 设置嵌入模型
            Settings.embed_model = OpenAIEmbedding(
                api_key=self.openai_api_key,
                model=embedding_model
            )
            
            logger.info(f"LlamaIndex配置完成: LLM={model_name}, Embedding={embedding_model}")
        except Exception as e:
            logger.error(f"LlamaIndex配置失败: {str(e)}")
            raise
    
    def create_index(self, documents: List[Document], force_rebuild: bool = False) -> VectorStoreIndex:
        """创建索引"""
        try:
            if not documents:
                logger.warning("没有文档可以索引")
                return None
            
            logger.info("创建内存向量索引...")
            
            # 创建简单的内存向量索引
            self.index = VectorStoreIndex.from_documents(
                documents=documents,
                show_progress=True
            )
            
            self.documents = documents
            logger.info(f"索引创建完成，包含 {len(documents)} 个文档")
            return self.index
            
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            raise
    
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
        
        return self.index.as_query_engine(**kwargs)
    
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
                    'content': node.text,
                    'score': getattr(node, 'score', 0.0),
                    'metadata': node.metadata or {}
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
            "index_type": "VectorStoreIndex (Memory)"
        }
