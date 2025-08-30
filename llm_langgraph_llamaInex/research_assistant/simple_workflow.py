"""
简化的工作流模块，不依赖 LangGraph
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SimpleWorkflow:
    """简化的工作流，不使用 LangGraph"""
    
    def __init__(self, index_manager, max_iterations: int = 3, enable_cache: bool = True):
        """初始化简化工作流"""
        self.index_manager = index_manager
        self.max_iterations = max_iterations
        self.enable_cache = enable_cache
        
        logger.info(f"简化工作流初始化完成: max_iterations={max_iterations}, enable_cache={enable_cache}")
    
    def run_research(self, query: str) -> Dict[str, Any]:
        """执行研究查询"""
        try:
            # 1. 检索相关文档
            relevant_docs = self.index_manager.search_similar(query, top_k=5)
            
            # 2. 使用查询引擎生成回答
            query_engine = self.index_manager.get_query_engine()
            response = query_engine.query(query)
            
            # 3. 构造结果
            result = {
                "query": query,
                "answer": str(response),
                "source_documents": relevant_docs,
                "confidence": 0.8  # 简化的置信度
            }
            
            logger.info(f"研究查询完成: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"研究查询失败: {str(e)}")
            return {
                "query": query,
                "answer": f"抱歉，查询过程中出现错误: {str(e)}",
                "source_documents": [],
                "confidence": 0.0
            }
    
    def chat(self, message: str, history: List[Dict] = None) -> str:
        """简化的聊天功能"""
        try:
            result = self.run_research(message)
            return result["answer"]
        except Exception as e:
            logger.error(f"聊天失败: {str(e)}")
            return f"抱歉，我无法处理您的问题: {str(e)}"
