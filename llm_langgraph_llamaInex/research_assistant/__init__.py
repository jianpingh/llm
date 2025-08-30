"""
研究助手模块
纯 LangGraph 实现，避免版本冲突
"""

__version__ = "1.0.0"
__author__ = "Research Assistant"

# 仅导入纯 LangGraph 组件
from .pure_langgraph_system import LangGraphRAGSystem, LangGraphDocumentProcessor, LangGraphVectorStore
from .langgraph_workflow import LangGraphResearchWorkflow, WorkflowConfig

__all__ = [
    "LangGraphRAGSystem",
    "LangGraphDocumentProcessor", 
    "LangGraphVectorStore",
    "LangGraphResearchWorkflow",
    "WorkflowConfig"
]
