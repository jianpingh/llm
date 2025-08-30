"""
优化的 LangGraph 工作流实现
与 LlamaIndex 完美集成
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass

# LangGraph 导入
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain 导入
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

logger = logging.getLogger(__name__)


class ResearchState(TypedDict):
    """研究状态定义"""
    query: str
    context: List[str]
    analysis: str
    response: str
    sources: List[Dict[str, Any]]
    step_count: int
    metadata: Dict[str, Any]


@dataclass
class WorkflowConfig:
    """工作流配置"""
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000
    max_steps: int = 5
    enable_memory: bool = True


class LangGraphResearchWorkflow:
    """基于 LangGraph 的研究工作流"""
    
    def __init__(self, 
                 index_manager,
                 openai_api_key: str,
                 config: WorkflowConfig = None):
        """初始化工作流"""
        self.index_manager = index_manager
        self.openai_api_key = openai_api_key
        self.config = config or WorkflowConfig()
        
        # 初始化组件
        self.llm = self._create_llm()
        self.workflow = self._build_workflow()
        
        logger.info("LangGraph 研究工作流初始化完成")
    
    def _create_llm(self):
        """创建语言模型"""
        return ChatOpenAI(
            api_key=self.openai_api_key,
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
    
    def _build_workflow(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(ResearchState)
        
        # 添加节点
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("validate_response", self._validate_response)
        
        # 定义边
        workflow.add_edge("retrieve_context", "analyze_query")
        workflow.add_edge("analyze_query", "generate_response")
        workflow.add_edge("generate_response", "validate_response")
        
        # 设置入口点
        workflow.set_entry_point("retrieve_context")
        
        # 添加条件边
        def should_continue(state: ResearchState) -> str:
            if state["step_count"] >= self.config.max_steps:
                return END
            
            # 检查响应质量
            response_length = len(state.get("response", ""))
            if response_length > 50:  # 基本长度检查
                return END
            else:
                return "analyze_query"
        
        workflow.add_conditional_edges(
            "validate_response",
            should_continue,
            {
                END: END,
                "analyze_query": "analyze_query"
            }
        )
        
        # 配置内存（如果启用）
        memory = MemorySaver() if self.config.enable_memory else None
        
        return workflow.compile(checkpointer=memory)
    
    def _retrieve_context(self, state: ResearchState) -> ResearchState:
        """检索相关上下文"""
        try:
            query = state["query"]
            logger.info(f"检索查询相关上下文: {query}")
            
            # 使用索引管理器搜索（支持不同类型的管理器）
            if hasattr(self.index_manager, 'search_similar'):
                results = self.index_manager.search_similar(query, top_k=5)
            elif hasattr(self.index_manager, 'similarity_search'):
                results = self.index_manager.similarity_search(query, k=5)
            else:
                logger.error("索引管理器缺少搜索方法")
                results = []
            
            # 提取上下文文本
            context = []
            sources = []
            
            for result in results:
                if isinstance(result, dict):
                    # 处理字典格式的结果
                    content = result.get("content", "")
                    score = result.get("score", 0.0)
                    metadata = result.get("metadata", {})
                else:
                    # 处理其他格式的结果
                    content = str(result)
                    score = 0.0
                    metadata = {}
                
                if content:
                    context.append(content)
                    sources.append({
                        "content": content[:200] + "..." if len(content) > 200 else content,
                        "score": score,
                        "metadata": metadata
                    })
            
            # 更新状态
            state["context"] = context
            state["sources"] = sources
            state["step_count"] = state.get("step_count", 0) + 1
            
            logger.info(f"检索到 {len(context)} 个相关文档")
            return state
            
        except Exception as e:
            logger.error(f"上下文检索失败: {str(e)}")
            state["context"] = []
            state["sources"] = []
            state["step_count"] = state.get("step_count", 0) + 1
            return state
    
    def _analyze_query(self, state: ResearchState) -> ResearchState:
        """分析查询意图"""
        try:
            query = state["query"]
            context = state.get("context", [])
            
            # 创建分析提示
            analysis_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的研究分析师。分析用户查询的意图和上下文信息，提供深入的分析。

基于提供的上下文信息，分析以下查询：
查询: {query}

上下文信息:
{context}

请提供：
1. 查询意图分析
2. 关键信息要点
3. 可能的研究方向
4. 需要重点关注的方面

保持分析简洁但全面。"""),
                ("human", "请分析这个查询。")
            ])
            
            # 准备上下文
            context_text = "\n\n".join(context[:3]) if context else "暂无相关上下文"
            
            # 执行分析
            chain = analysis_prompt | self.llm
            result = chain.invoke({
                "query": query,
                "context": context_text
            })
            
            analysis = result.content if hasattr(result, 'content') else str(result)
            
            # 更新状态
            state["analysis"] = analysis
            state["step_count"] = state.get("step_count", 0) + 1
            
            logger.info("查询分析完成")
            return state
            
        except Exception as e:
            logger.error(f"查询分析失败: {str(e)}")
            state["analysis"] = "分析失败，将基于可用信息回答"
            return state
    
    def _generate_response(self, state: ResearchState) -> ResearchState:
        """生成回应"""
        try:
            query = state["query"]
            context = state.get("context", [])
            analysis = state.get("analysis", "")
            
            # 创建响应提示
            response_prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个知识渊博的研究助手。基于分析结果和上下文信息，为用户查询提供准确、详细、有用的回答。

查询: {query}

分析结果:
{analysis}

上下文信息:
{context}

请提供：
1. 直接回答用户问题
2. 详细的解释和说明
3. 相关的例子或案例
4. 实用的建议或建议

确保回答准确、清晰、有帮助。如果信息不足，请明确说明限制。"""),
                ("human", "请基于分析和上下文回答我的问题。")
            ])
            
            # 准备上下文
            context_text = "\n\n".join(context) if context else "暂无相关上下文"
            
            # 生成响应
            chain = response_prompt | self.llm
            result = chain.invoke({
                "query": query,
                "analysis": analysis,
                "context": context_text
            })
            
            response = result.content if hasattr(result, 'content') else str(result)
            
            # 更新状态
            state["response"] = response
            state["step_count"] = state.get("step_count", 0) + 1
            
            logger.info("响应生成完成")
            return state
            
        except Exception as e:
            logger.error(f"响应生成失败: {str(e)}")
            state["response"] = f"抱歉，生成回答时遇到问题: {str(e)}"
            return state
    
    def _validate_response(self, state: ResearchState) -> ResearchState:
        """验证响应质量"""
        try:
            response = state.get("response", "")
            query = state["query"]
            
            # 基本质量检查
            if len(response) < 50:
                state["metadata"] = {
                    "quality_score": 0.3,
                    "needs_improvement": True,
                    "reason": "回答过短"
                }
            elif "抱歉" in response or "无法" in response:
                state["metadata"] = {
                    "quality_score": 0.5,
                    "needs_improvement": True,
                    "reason": "回答不够完整"
                }
            else:
                state["metadata"] = {
                    "quality_score": 0.8,
                    "needs_improvement": False,
                    "reason": "回答质量良好"
                }
            
            state["step_count"] = state.get("step_count", 0) + 1
            
            logger.info(f"响应验证完成，质量分数: {state['metadata']['quality_score']}")
            return state
            
        except Exception as e:
            logger.error(f"响应验证失败: {str(e)}")
            state["metadata"] = {"quality_score": 0.1, "error": str(e)}
            return state
    
    def process_query(self, query: str, thread_id: str = None) -> Dict[str, Any]:
        """处理查询"""
        try:
            logger.info(f"开始处理查询: {query}")
            
            # 初始状态
            initial_state = {
                "query": query,
                "context": [],
                "analysis": "",
                "response": "",
                "sources": [],
                "step_count": 0,
                "metadata": {}
            }
            
            # 配置运行参数
            config = {"thread_id": thread_id} if thread_id else None
            
            # 执行工作流
            result = self.workflow.invoke(initial_state, config=config)
            
            logger.info("查询处理完成")
            return {
                "query": result["query"],
                "response": result["response"],
                "sources": result["sources"],
                "analysis": result["analysis"],
                "metadata": result["metadata"],
                "step_count": result["step_count"]
            }
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return {
                "query": query,
                "response": f"处理查询时遇到错误: {str(e)}",
                "sources": [],
                "analysis": "",
                "metadata": {"error": str(e)},
                "step_count": 0
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """获取工作流信息"""
        return {
            "workflow_type": "LangGraph Research Workflow",
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_steps": self.config.max_steps,
            "enable_memory": self.config.enable_memory,
            "nodes": ["retrieve_context", "analyze_query", "generate_response", "validate_response"],
            "status": "Ready"
        }
