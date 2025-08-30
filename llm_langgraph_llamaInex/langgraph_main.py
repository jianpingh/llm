"""
LangGraph + LlamaIndex 完美集成的研究助手应用
使用兼容版本实现复杂推理工作流
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入配置
from config import config

# 导入项目组件
from research_assistant.document_processor import DocumentProcessor
from research_assistant.langgraph_index_manager import LangGraphIndexManager
from research_assistant.langgraph_workflow import LangGraphResearchWorkflow, WorkflowConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LangGraphResearchApp:
    """LangGraph + LlamaIndex 集成研究应用"""
    
    def __init__(self):
        """初始化应用"""
        self.config = config
        self.document_processor = None
        self.index_manager = None
        self.workflow = None
        
        # 确保日志目录存在
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("LangGraph + LlamaIndex 研究助手启动")
        logger.info("=" * 60)
        
        # 初始化组件
        self._initialize_components()
        
        logger.info("应用初始化完成")
    
    def _initialize_components(self):
        """初始化所有组件"""
        try:
            # 1. 初始化文档处理器
            logger.info("初始化文档处理器...")
            self.document_processor = DocumentProcessor()
            
            # 2. 初始化索引管理器
            logger.info("初始化 LangGraph 兼容索引管理器...")
            self.index_manager = LangGraphIndexManager(
                persist_dir=self.config.INDEX.PERSIST_DIR,
                openai_api_key=self.config.OPENAI.API_KEY,
                model_name=self.config.OPENAI.MODEL_NAME,
                embedding_model=self.config.OPENAI.EMBEDDING_MODEL,
                top_k=self.config.INDEX.TOP_K
            )
            
            # 3. 初始化 LangGraph 工作流
            logger.info("初始化 LangGraph 研究工作流...")
            workflow_config = WorkflowConfig(
                model_name=self.config.OPENAI.MODEL_NAME,
                temperature=self.config.OPENAI.TEMPERATURE,
                max_tokens=self.config.OPENAI.MAX_TOKENS,
                max_steps=5,
                enable_memory=True
            )
            
            self.workflow = LangGraphResearchWorkflow(
                index_manager=self.index_manager,
                openai_api_key=self.config.OPENAI.API_KEY,
                config=workflow_config
            )
            
            logger.info("所有组件初始化成功")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {str(e)}")
            raise
    
    def setup_documents(self, documents_dir: str = "./sample_documents") -> Dict[str, Any]:
        """设置文档索引"""
        try:
            logger.info(f"开始处理文档目录: {documents_dir}")
            
            # 检查目录是否存在
            doc_path = Path(documents_dir)
            if not doc_path.exists():
                raise FileNotFoundError(f"文档目录不存在: {documents_dir}")
            
            # 处理文档
            documents = self.document_processor.process_directory(documents_dir)
            
            if not documents:
                logger.warning("没有找到可处理的文档")
                return {"status": "warning", "message": "没有找到可处理的文档"}
            
            logger.info(f"成功处理 {len(documents)} 个文档")
            
            # 创建索引
            logger.info("创建向量索引...")
            index = self.index_manager.create_index(documents)
            
            if index:
                stats = self.index_manager.get_index_stats()
                logger.info(f"索引创建成功: {stats}")
                return {
                    "status": "success",
                    "message": f"成功处理 {len(documents)} 个文档并创建索引",
                    "stats": stats
                }
            else:
                return {"status": "error", "message": "索引创建失败"}
                
        except Exception as e:
            logger.error(f"文档设置失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def query(self, question: str, thread_id: str = None) -> Dict[str, Any]:
        """处理查询"""
        try:
            logger.info(f"处理查询: {question}")
            
            if not self.workflow:
                raise ValueError("工作流未初始化")
            
            # 使用 LangGraph 工作流处理查询
            result = self.workflow.process_query(question, thread_id=thread_id)
            
            logger.info("查询处理完成")
            return result
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return {
                "query": question,
                "response": f"查询处理失败: {str(e)}",
                "sources": [],
                "analysis": "",
                "metadata": {"error": str(e)},
                "step_count": 0
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            status = {
                "application": "LangGraph + LlamaIndex 研究助手",
                "status": "运行中",
                "components": {
                    "document_processor": {
                        "status": "已初始化" if self.document_processor else "未初始化",
                        "supported_types": getattr(self.document_processor, 'supported_types', []) if self.document_processor else []
                    },
                    "index_manager": {
                        "status": "已初始化" if self.index_manager else "未初始化",
                        "stats": self.index_manager.get_index_stats() if self.index_manager else {}
                    },
                    "workflow": {
                        "status": "已初始化" if self.workflow else "未初始化",
                        "info": self.workflow.get_workflow_info() if self.workflow else {}
                    }
                },
                "configuration": {
                    "model": self.config.OPENAI.MODEL_NAME,
                    "embedding_model": self.config.OPENAI.EMBEDDING_MODEL,
                    "environment": self.config.ENVIRONMENT,
                    "index_persist_dir": self.config.INDEX.PERSIST_DIR
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def reset_index(self) -> Dict[str, Any]:
        """重置索引"""
        try:
            logger.info("重置索引...")
            
            # 重新初始化索引管理器
            self.index_manager = LangGraphIndexManager(
                persist_dir=self.config.INDEX.PERSIST_DIR,
                openai_api_key=self.config.OPENAI.API_KEY,
                model_name=self.config.OPENAI.MODEL_NAME,
                embedding_model=self.config.OPENAI.EMBEDDING_MODEL,
                top_k=self.config.INDEX.TOP_K
            )
            
            logger.info("索引重置完成")
            return {"status": "success", "message": "索引已重置"}
            
        except Exception as e:
            logger.error(f"索引重置失败: {str(e)}")
            return {"status": "error", "message": str(e)}


def main():
    """主函数"""
    try:
        # 创建应用实例
        app = LangGraphResearchApp()
        
        # 显示系统状态
        status = app.get_system_status()
        print("\n" + "=" * 60)
        print("系统状态:")
        print("=" * 60)
        print(f"应用: {status['application']}")
        print(f"状态: {status['status']}")
        print(f"环境: {status['configuration']['environment']}")
        print(f"模型: {status['configuration']['model']}")
        print(f"嵌入模型: {status['configuration']['embedding_model']}")
        
        # 设置文档
        print("\n" + "-" * 40)
        print("设置文档索引...")
        print("-" * 40)
        
        setup_result = app.setup_documents()
        print(f"设置结果: {setup_result['status']}")
        print(f"消息: {setup_result['message']}")
        
        if setup_result['status'] == 'success':
            # 测试查询
            print("\n" + "-" * 40)
            print("测试 LangGraph 工作流...")
            print("-" * 40)
            
            test_queries = [
                "什么是 LangGraph？它有什么主要特点？",
                "LlamaIndex 如何帮助处理文档？",
                "如何结合使用 LangGraph 和 LlamaIndex？"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n查询 {i}: {query}")
                print("-" * 20)
                
                result = app.query(query)
                print(f"回答: {result['response'][:200]}...")
                print(f"步骤数: {result['step_count']}")
                print(f"来源数量: {len(result['sources'])}")
                
                if result['metadata']:
                    quality_score = result['metadata'].get('quality_score', 'N/A')
                    print(f"质量分数: {quality_score}")
        
        print("\n" + "=" * 60)
        print("应用运行完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n应用被用户中断")
    except Exception as e:
        logger.error(f"应用运行失败: {str(e)}")
        print(f"\n错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()
