"""
聊天界面模块
提供用户交互界面和会话管理
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatInterface:
    """聊天界面管理器"""
    
    def __init__(self, research_workflow):
        """
        初始化聊天界面
        
        Args:
            research_workflow: 研究工作流实例
        """
        self.research_workflow = research_workflow
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"聊天界面初始化完成，会话ID: {self.session_id}")
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入并返回响应
        
        Args:
            user_input: 用户输入
            
        Returns:
            聊天响应
        """
        try:
            # 记录用户输入
            self._add_to_history("user", user_input)
            
            # 运行研究工作流
            result = self.research_workflow.run(user_input)
            
            # 记录助手响应
            self._add_to_history("assistant", result["answer"])
            
            # 构建响应
            response = {
                "answer": result["answer"],
                "confidence": result["confidence"],
                "strategy": result.get("strategy", "unknown"),
                "retrieved_docs_count": result.get("retrieved_docs_count", 0),
                "iterations": result.get("iterations", 0),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "success": result.get("success", True)
            }
            
            if not result.get("success", True):
                response["error"] = result.get("error", "未知错误")
            
            logger.info(f"聊天响应生成完成，置信度: {result['confidence']:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"聊天处理失败: {str(e)}")
            error_response = {
                "answer": "抱歉，处理您的请求时发生了错误。请稍后重试。",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "success": False
            }
            self._add_to_history("assistant", error_response["answer"])
            return error_response
    
    async def achat(self, user_input: str) -> Dict[str, Any]:
        """
        异步处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            聊天响应
        """
        try:
            # 记录用户输入
            self._add_to_history("user", user_input)
            
            # 异步运行研究工作流
            result = await self.research_workflow.arun(user_input)
            
            # 记录助手响应
            self._add_to_history("assistant", result["answer"])
            
            # 构建响应
            response = {
                "answer": result["answer"],
                "confidence": result["confidence"],
                "strategy": result.get("strategy", "unknown"),
                "retrieved_docs_count": result.get("retrieved_docs_count", 0),
                "iterations": result.get("iterations", 0),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "success": result.get("success", True)
            }
            
            if not result.get("success", True):
                response["error"] = result.get("error", "未知错误")
            
            logger.info(f"异步聊天响应生成完成，置信度: {result['confidence']:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"异步聊天处理失败: {str(e)}")
            error_response = {
                "answer": "抱歉，处理您的请求时发生了错误。请稍后重试。",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "success": False
            }
            self._add_to_history("assistant", error_response["answer"])
            return error_response
    
    def _add_to_history(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史记录长度
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info("对话历史已清空")
    
    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        return {
            "session_id": self.session_id,
            "message_count": len(self.conversation_history),
            "start_time": self.session_id,
            "last_activity": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def export_conversation(self, format: str = "json") -> str:
        """
        导出对话记录
        
        Args:
            format: 导出格式 ("json" 或 "text")
            
        Returns:
            导出的对话记录
        """
        if format == "json":
            import json
            return json.dumps(self.conversation_history, ensure_ascii=False, indent=2)
        
        elif format == "text":
            lines = []
            for msg in self.conversation_history:
                role = "用户" if msg["role"] == "user" else "助手"
                time = msg["timestamp"]
                content = msg["content"]
                lines.append(f"[{time}] {role}: {content}")
            return "\n\n".join(lines)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """获取聊天统计信息"""
        if not self.conversation_history:
            return {"total_messages": 0}
        
        user_messages = [msg for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg for msg in self.conversation_history if msg["role"] == "assistant"]
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_duration": self._calculate_session_duration(),
            "average_response_length": self._calculate_avg_response_length(assistant_messages)
        }
    
    def _calculate_session_duration(self) -> str:
        """计算会话持续时间"""
        if len(self.conversation_history) < 2:
            return "0分钟"
        
        start_time = datetime.fromisoformat(self.conversation_history[0]["timestamp"])
        end_time = datetime.fromisoformat(self.conversation_history[-1]["timestamp"])
        duration = end_time - start_time
        
        minutes = int(duration.total_seconds() / 60)
        return f"{minutes}分钟"
    
    def _calculate_avg_response_length(self, assistant_messages: List[Dict[str, Any]]) -> int:
        """计算平均响应长度"""
        if not assistant_messages:
            return 0
        
        total_length = sum(len(msg["content"]) for msg in assistant_messages)
        return total_length // len(assistant_messages)
