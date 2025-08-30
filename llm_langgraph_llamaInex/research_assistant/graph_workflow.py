"""
LangGraph工作流模块
实现复杂的研究和问答工作流
"""

import os
import logging
from typing import Dict, Any, List, TypedDict, Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """研究工作流状态定义"""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    retrieved_docs: List[Dict[str, Any]]
    analysis_result: str
    final_answer: str
    confidence_score: float
    search_strategy: str
    iteration_count: int


class ResearchWorkflow:
    """研究工作流，使用LangGraph实现复杂的多步推理"""
    
    def __init__(self, index_manager, max_iterations: int = 3, enable_cache: bool = True):
        """
        初始化研究工作流
        
        Args:
            index_manager: 索引管理器实例
            max_iterations: 最大迭代次数
            enable_cache: 是否启用缓存
        """
        self.index_manager = index_manager
        self.max_iterations = max_iterations
        self.enable_cache = enable_cache
        self.workflow = self._build_workflow()
        
        logger.info(f"研究工作流初始化完成: max_iterations={max_iterations}, enable_cache={enable_cache}")
    
    def _build_workflow(self) -> StateGraph:
        """构建LangGraph工作流"""
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("query_analysis", self._analyze_query)
        workflow.add_node("document_retrieval", self._retrieve_documents)
        workflow.add_node("content_analysis", self._analyze_content)
        workflow.add_node("answer_generation", self._generate_answer)
        workflow.add_node("quality_check", self._check_quality)
        workflow.add_node("refinement", self._refine_search)
        
        # 设置入口点
        workflow.set_entry_point("query_analysis")
        
        # 添加边
        workflow.add_edge("query_analysis", "document_retrieval")
        workflow.add_edge("document_retrieval", "content_analysis")
        workflow.add_edge("content_analysis", "answer_generation")
        workflow.add_edge("answer_generation", "quality_check")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "quality_check",
            self._should_refine,
            {
                "refine": "refinement",
                "end": END
            }
        )
        workflow.add_edge("refinement", "document_retrieval")
        
        return workflow.compile()
    
    def _analyze_query(self, state: ResearchState) -> ResearchState:
        """分析查询意图和策略"""
        query = state["query"]
        
        # 简单的查询分析逻辑
        if "比较" in query or "对比" in query:
            strategy = "comparative"
        elif "总结" in query or "概述" in query:
            strategy = "summarization"
        elif "如何" in query or "怎么" in query:
            strategy = "how_to"
        elif "为什么" in query or "原因" in query:
            strategy = "causal"
        else:
            strategy = "general"
        
        logger.info(f"查询分析完成，策略: {strategy}")
        
        return {
            **state,
            "search_strategy": strategy,
            "iteration_count": 0
        }
    
    def _retrieve_documents(self, state: ResearchState) -> ResearchState:
        """检索相关文档"""
        query = state["query"]
        strategy = state["search_strategy"]
        iteration = state.get("iteration_count", 0)
        
        # 根据策略调整检索参数
        if strategy == "comparative":
            top_k = 8
        elif strategy == "summarization":
            top_k = 10
        else:
            top_k = 5
        
        # 如果是重新检索，增加多样性
        if iteration > 0:
            top_k += 3
        
        try:
            retrieved_docs = self.index_manager.search_similar(query, top_k=top_k)
            logger.info(f"检索到 {len(retrieved_docs)} 个相关文档")
            
            return {
                **state,
                "retrieved_docs": retrieved_docs
            }
            
        except Exception as e:
            logger.error(f"文档检索失败: {str(e)}")
            return {
                **state,
                "retrieved_docs": []
            }
    
    def _analyze_content(self, state: ResearchState) -> ResearchState:
        """分析检索到的内容"""
        docs = state["retrieved_docs"]
        strategy = state["search_strategy"]
        
        if not docs:
            analysis = "未找到相关文档内容"
        else:
            # 根据策略分析内容
            if strategy == "comparative":
                analysis = self._comparative_analysis(docs)
            elif strategy == "summarization":
                analysis = self._summarization_analysis(docs)
            else:
                analysis = self._general_analysis(docs)
        
        logger.info("内容分析完成")
        
        return {
            **state,
            "analysis_result": analysis
        }
    
    def _comparative_analysis(self, docs: List[Dict[str, Any]]) -> str:
        """比较分析"""
        content_pieces = [doc["text"][:500] for doc in docs[:4]]
        return f"比较分析基于 {len(content_pieces)} 个文档片段的内容"
    
    def _summarization_analysis(self, docs: List[Dict[str, Any]]) -> str:
        """总结分析"""
        total_content = " ".join([doc["text"][:300] for doc in docs])
        return f"总结分析基于 {len(docs)} 个文档，总计 {len(total_content)} 字符"
    
    def _general_analysis(self, docs: List[Dict[str, Any]]) -> str:
        """一般分析"""
        return f"一般分析基于 {len(docs)} 个相关文档的内容"
    
    def _generate_answer(self, state: ResearchState) -> ResearchState:
        """生成答案"""
        query = state["query"]
        docs = state["retrieved_docs"]
        analysis = state["analysis_result"]
        
        if not docs:
            answer = "抱歉，我无法在文档中找到相关信息来回答您的问题。"
            confidence = 0.1
        else:
            # 使用LlamaIndex查询引擎生成答案
            try:
                query_engine = self.index_manager.get_query_engine()
                response = query_engine.query(query)
                answer = str(response)
                
                # 简单的置信度计算
                confidence = min(0.9, len(docs) * 0.15)
                
                logger.info("答案生成完成")
                
            except Exception as e:
                logger.error(f"答案生成失败: {str(e)}")
                answer = "生成答案时发生错误，请稍后重试。"
                confidence = 0.1
        
        return {
            **state,
            "final_answer": answer,
            "confidence_score": confidence
        }
    
    def _check_quality(self, state: ResearchState) -> ResearchState:
        """检查答案质量"""
        confidence = state["confidence_score"]
        answer = state["final_answer"]
        iteration = state.get("iteration_count", 0)
        
        # 质量检查逻辑
        quality_issues = []
        
        if confidence < 0.5:
            quality_issues.append("置信度过低")
        
        if len(answer) < 50:
            quality_issues.append("答案过短")
        
        if "抱歉" in answer or "无法" in answer:
            quality_issues.append("答案表示无法回答")
        
        logger.info(f"质量检查完成，发现 {len(quality_issues)} 个问题")
        
        return state
    
    def _should_refine(self, state: ResearchState) -> str:
        """决定是否需要优化搜索"""
        confidence = state["confidence_score"]
        iteration = state.get("iteration_count", 0)
        
        # 如果置信度低且未达到最大迭代次数，则优化
        if confidence < 0.6 and iteration < self.max_iterations:
            return "refine"
        else:
            return "end"
    
    def _refine_search(self, state: ResearchState) -> ResearchState:
        """优化搜索策略"""
        iteration = state.get("iteration_count", 0)
        new_iteration = iteration + 1
        
        logger.info(f"开始第 {new_iteration} 次搜索优化")
        
        return {
            **state,
            "iteration_count": new_iteration
        }
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        运行研究工作流
        
        Args:
            query: 用户查询
            
        Returns:
            研究结果
        """
        try:
            # 初始化状态
            initial_state = ResearchState(
                messages=[HumanMessage(content=query)],
                query=query,
                retrieved_docs=[],
                analysis_result="",
                final_answer="",
                confidence_score=0.0,
                search_strategy="general",
                iteration_count=0
            )
            
            # 运行工作流
            result = self.workflow.invoke(initial_state)
            
            logger.info("研究工作流执行完成")
            
            return {
                "query": query,
                "answer": result["final_answer"],
                "confidence": result["confidence_score"],
                "strategy": result["search_strategy"],
                "retrieved_docs_count": len(result["retrieved_docs"]),
                "iterations": result["iteration_count"],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            return {
                "query": query,
                "answer": "执行过程中发生错误，请稍后重试。",
                "confidence": 0.0,
                "error": str(e),
                "success": False
            }
    
    async def arun(self, query: str) -> Dict[str, Any]:
        """
        异步运行研究工作流
        
        Args:
            query: 用户查询
            
        Returns:
            研究结果
        """
        try:
            # 初始化状态
            initial_state = ResearchState(
                messages=[HumanMessage(content=query)],
                query=query,
                retrieved_docs=[],
                analysis_result="",
                final_answer="",
                confidence_score=0.0,
                search_strategy="general",
                iteration_count=0
            )
            
            # 异步运行工作流
            result = await self.workflow.ainvoke(initial_state)
            
            logger.info("异步研究工作流执行完成")
            
            return {
                "query": query,
                "answer": result["final_answer"],
                "confidence": result["confidence_score"],
                "strategy": result["search_strategy"],
                "retrieved_docs_count": len(result["retrieved_docs"]),
                "iterations": result["iteration_count"],
                "success": True
            }
            
        except Exception as e:
            logger.error(f"异步工作流执行失败: {str(e)}")
            return {
                "query": query,
                "answer": "执行过程中发生错误，请稍后重试。",
                "confidence": 0.0,
                "error": str(e),
                "success": False
            }
