"""
智能研究助手主程序
LangGraph + LlamaIndex + OpenAI 集成示例
"""

import os
import logging
from pathlib import Path
from typing import Optional

from config import get_config, EnvironmentConfig
from research_assistant import DocumentProcessor, IndexManager, ResearchWorkflow, ChatInterface

logger = logging.getLogger(__name__)


class ResearchAssistantApp:
    """智能研究助手应用"""
    
    def __init__(self, environment: Optional[str] = None):
        """
        初始化应用
        
        Args:
            environment: 环境名称 (development, staging, production)
        """
        # 加载配置
        if environment:
            from config import switch_environment
            self.config = switch_environment(environment)
        else:
            self.config = get_config()
        
        # 配置日志
        self._setup_logging()
        
        # 验证配置
        self._validate_config()
        
        # 初始化组件
        self._initialize_components()
    
    def _setup_logging(self):
        """配置日志"""
        app_config = self.config.get_app_config()
        
        # 创建日志目录
        log_file = Path(app_config['log_file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志级别
        log_level = getattr(logging, app_config['log_level'].upper(), logging.INFO)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 清除现有处理器
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 配置根日志器
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler],
            force=True
        )
        
        logger.info(f"日志系统已配置: 级别={app_config['log_level']}, 文件={log_file}")
    
    def _validate_config(self):
        """验证配置"""
        validation = self.config.validate_config()
        if not validation['valid']:
            logger.error("配置验证失败:")
            for issue in validation['issues']:
                logger.error(f"  - {issue}")
            raise ValueError("配置验证失败，请检查配置文件")
        
        logger.info(f"配置验证通过 (环境: {validation['environment']})")
    
    def _initialize_components(self):
        """初始化组件"""
        # 获取配置
        openai_config = self.config.get_openai_config()
        vector_config = self.config.get_vector_db_config()
        doc_config = self.config.get_document_config()
        workflow_config = self.config.get_workflow_config()
        retrieval_config = self.config.get_retrieval_config()
        
        # 创建必要目录
        Path(doc_config['documents_dir']).mkdir(parents=True, exist_ok=True)
        Path(doc_config['temp_dir']).mkdir(parents=True, exist_ok=True)
        
        # 初始化文档处理器
        self.doc_processor = DocumentProcessor(
            chunk_size=doc_config['chunk_size'],
            chunk_overlap=doc_config['chunk_overlap'],
            supported_types=doc_config['supported_types']
        )
        
        # 初始化索引管理器 - 使用最小化版本避免版本冲突
        from research_assistant.minimal_index_manager import MinimalIndexManager
        self.index_manager = MinimalIndexManager(
            persist_dir=vector_config.get('persist_directory', './indexes/simple_db'),
            openai_api_key=openai_config['api_key'],
            model_name=openai_config['model'],
            embedding_model=openai_config['embedding_model'],
            top_k=retrieval_config['top_k'],
            similarity_threshold=retrieval_config['similarity_threshold']
        )
        
        # 初始化工作流 - 使用简化版本避免版本冲突
        from research_assistant.simple_workflow import SimpleWorkflow
        self.workflow = SimpleWorkflow(
            index_manager=self.index_manager,
            max_iterations=workflow_config['max_iterations'],
            enable_cache=workflow_config['enable_cache']
        )
        
        # 初始化聊天界面
        self.chat_interface = ChatInterface(self.workflow)
        
        logger.info("研究助手应用初始化完成")
    
    def initialize_knowledge_base(self, data_dir: str = "./data", force_rebuild: bool = False):
        """
        初始化知识库
        
        Args:
            data_dir: 数据目录
            force_rebuild: 是否强制重建
        """
        logger.info("开始初始化知识库...")
        
        # 加载文档
        documents = self.doc_processor.load_documents(data_dir)
        
        if not documents:
            logger.warning("未找到任何文档")
            return
        
        # 分割文档
        split_documents = self.doc_processor.split_documents(documents)
        
        # 创建索引
        self.index_manager.create_index(split_documents, force_rebuild=force_rebuild)
        
        # 显示统计信息
        doc_stats = self.doc_processor.get_document_stats(split_documents)
        index_stats = self.index_manager.get_index_stats()
        
        logger.info("知识库初始化完成")
        logger.info(f"文档统计: {doc_stats}")
        logger.info(f"索引统计: {index_stats}")
    
    def run_interactive_mode(self):
        """运行交互模式"""
        print("=" * 60)
        print("🤖 智能研究助手")
        print("集成 LangGraph + LlamaIndex + OpenAI")
        print("=" * 60)
        print("输入 'quit' 或 'exit' 退出")
        print("输入 'help' 查看帮助")
        print("输入 'stats' 查看统计信息")
        print("输入 'clear' 清空对话历史")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("👋 再见！")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                elif user_input.lower() == 'stats':
                    self._show_statistics()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.chat_interface.clear_history()
                    print("🗑️ 对话历史已清空")
                    continue
                
                # 处理用户问题
                print("🤔 思考中...")
                response = self.chat_interface.chat(user_input)
                
                # 显示回答
                print(f"\n🤖 助手: {response['answer']}")
                
                # 显示置信度和其他信息
                if response.get('success', True):
                    print(f"\n📊 置信度: {response['confidence']:.1%}")
                    print(f"🔍 策略: {response['strategy']}")
                    print(f"📚 检索文档: {response['retrieved_docs_count']} 个")
                    if response['iterations'] > 0:
                        print(f"🔄 优化迭代: {response['iterations']} 次")
                else:
                    print(f"❌ 错误: {response.get('error', '未知错误')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                logger.error(f"交互模式错误: {str(e)}")
                print(f"❌ 发生错误: {str(e)}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
📖 帮助信息:

支持的命令:
- quit/exit: 退出程序
- help: 显示此帮助信息
- stats: 显示统计信息
- clear: 清空对话历史

支持的问题类型:
- 总结性问题: "请总结..."、"概述..."
- 比较性问题: "比较..."、"对比..."
- 方法性问题: "如何..."、"怎么..."
- 原因性问题: "为什么..."、"原因是..."
- 一般性问题: 其他任何问题

使用技巧:
- 问题越具体，答案越准确
- 可以要求比较不同概念或方法
- 可以询问具体的操作步骤
- 支持中英文混合提问
        """
        print(help_text)
    
    def _show_statistics(self):
        """显示统计信息"""
        index_stats = self.index_manager.get_index_stats()
        chat_stats = self.chat_interface.get_chat_statistics()
        session_info = self.chat_interface.get_session_info()
        
        print("\n📊 统计信息:")
        print(f"📚 索引状态: {index_stats.get('status', '未知')}")
        print(f"📄 文档数量: {index_stats.get('document_count', 0)}")
        print(f"💬 总消息数: {chat_stats.get('total_messages', 0)}")
        print(f"👤 用户消息: {chat_stats.get('user_messages', 0)}")
        print(f"🤖 助手消息: {chat_stats.get('assistant_messages', 0)}")
        print(f"⏱️ 会话时长: {chat_stats.get('session_duration', '0分钟')}")
        print(f"📝 平均回复长度: {chat_stats.get('average_response_length', 0)} 字符")
        print(f"🆔 会话ID: {session_info['session_id']}")
    
    def ask_question(self, question: str) -> dict:
        """
        单次问答接口
        
        Args:
            question: 问题
            
        Returns:
            回答结果
        """
        return self.chat_interface.chat(question)


def main():
    """主函数"""
    try:
        # 创建应用实例
        app = ResearchAssistantApp()
        
        # 初始化知识库（如果数据目录存在）
        data_dir = "./data"
        if Path(data_dir).exists():
            app.initialize_knowledge_base(data_dir)
        else:
            logger.warning(f"数据目录 {data_dir} 不存在，请添加文档后重新运行")
            print(f"⚠️ 数据目录 {data_dir} 不存在")
            print("请将文档放入该目录后重新运行程序")
            return
        
        # 运行交互模式
        app.run_interactive_mode()
        
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        print(f"❌ 程序启动失败: {str(e)}")


if __name__ == "__main__":
    main()
