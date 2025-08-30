"""
简化的 LangGraph 演示应用
专注于核心工作流功能，最小化依赖冲突
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, TypedDict
import json
import re

# 核心依赖
from langchain_openai import ChatOpenAI

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入配置
from config import config

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


class SimpleState(TypedDict):
    """简化状态定义"""
    query: str
    documents: List[str]
    analysis: str
    response: str
    step_count: int


class SimpleDocumentLoader:
    """简单文档加载器"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.md', '.py', '.js', '.html']
    
    def load_documents(self, directory: str) -> List[str]:
        """加载目录中的文档"""
        documents = []
        doc_dir = Path(directory)
        
        if not doc_dir.exists():
            logger.error(f"目录不存在: {directory}")
            return documents
        
        for file_path in doc_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    content = self._read_file(file_path)
                    if content:
                        documents.append(f"文件: {file_path.name}\n内容: {content}")
                        logger.info(f"加载文档: {file_path.name}")
                except Exception as e:
                    logger.warning(f"读取文件失败 {file_path}: {str(e)}")
        
        logger.info(f"共加载 {len(documents)} 个文档")
        return documents
    
    def _read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:2000]  # 限制长度
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                return content[:2000]
            except:
                return ""


class SimpleLangGraphWorkflow:
    """简化的工作流实现"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        # 加载文档
        self.document_loader = SimpleDocumentLoader()
        self.documents = []
        
        logger.info("简化工作流初始化完成")
    
    def load_documents(self, directory: str = "./sample_documents") -> Dict[str, Any]:
        """加载文档"""
        try:
            self.documents = self.document_loader.load_documents(directory)
            return {
                "status": "success",
                "message": f"成功加载 {len(self.documents)} 个文档",
                "document_count": len(self.documents)
            }
        except Exception as e:
            logger.error(f"文档加载失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 3) -> List[str]:
        """简单的文档检索（基于关键词匹配）"""
        if not self.documents:
            return []
        
        # 简单的关键词匹配算法
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_docs = []
        
        for doc in self.documents:
            doc_words = set(re.findall(r'\w+', doc.lower()))
            score = len(query_words.intersection(doc_words))
            if score > 0:
                scored_docs.append((doc, score))
        
        # 按得分排序并返回top_k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:top_k]]
    
    def analyze_query(self, query: str, context_docs: List[str]) -> str:
        """分析查询"""
        try:
            context_text = "\n\n".join(context_docs[:2]) if context_docs else "无相关文档"
            
            prompt = f"""作为一个研究分析师，请分析以下查询：

查询: {query}

相关文档:
{context_text}

请提供：
1. 查询意图分析
2. 关键信息要点
3. 研究方向建议

保持分析简洁明了。"""

            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"查询分析失败: {str(e)}")
            return f"分析失败: {str(e)}"
    
    def generate_response(self, query: str, analysis: str, context_docs: List[str]) -> str:
        """生成最终回答"""
        try:
            context_text = "\n\n".join(context_docs) if context_docs else "无相关文档"
            
            prompt = f"""基于分析结果和相关文档，请为用户查询提供详细、准确的回答：

用户查询: {query}

分析结果: {analysis}

相关文档:
{context_text}

请提供：
1. 直接回答用户问题
2. 详细解释和说明  
3. 相关例子或建议
4. 总结要点

确保回答准确、有用、结构清晰。"""

            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"回答生成失败: {str(e)}")
            return f"抱歉，生成回答时遇到问题: {str(e)}"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """处理完整查询流程"""
        try:
            logger.info(f"处理查询: {query}")
            
            # Step 1: 检索相关文档
            logger.info("步骤1: 检索相关文档")
            relevant_docs = self.retrieve_relevant_docs(query)
            
            # Step 2: 分析查询
            logger.info("步骤2: 分析查询意图")
            analysis = self.analyze_query(query, relevant_docs)
            
            # Step 3: 生成回答
            logger.info("步骤3: 生成最终回答")
            response = self.generate_response(query, analysis, relevant_docs)
            
            result = {
                "query": query,
                "analysis": analysis,
                "response": response,
                "relevant_docs_count": len(relevant_docs),
                "step_count": 3,
                "status": "success"
            }
            
            logger.info("查询处理完成")
            return result
            
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            return {
                "query": query,
                "analysis": "",
                "response": f"处理查询时出错: {str(e)}",
                "relevant_docs_count": 0,
                "step_count": 0,
                "status": "error"
            }


class SimpleLangGraphApp:
    """简化的 LangGraph 应用"""
    
    def __init__(self):
        self.config = config
        self.workflow = None
        
        # 确保日志目录存在
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("简化 LangGraph 研究助手启动")
        logger.info("=" * 60)
        
        self._initialize()
    
    def _initialize(self):
        """初始化应用"""
        try:
            logger.info("初始化简化工作流...")
            
            # 获取OpenAI配置
            openai_config = self.config.get_openai_config()
            
            self.workflow = SimpleLangGraphWorkflow(
                openai_api_key=openai_config['api_key']
            )
            logger.info("应用初始化完成")
            
        except Exception as e:
            logger.error(f"应用初始化失败: {str(e)}")
            raise
    
    def setup_documents(self, documents_dir: str = "./sample_documents") -> Dict[str, Any]:
        """设置文档"""
        return self.workflow.load_documents(documents_dir)
    
    def query(self, question: str) -> Dict[str, Any]:
        """处理查询"""
        return self.workflow.process_query(question)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        openai_config = self.config.get_openai_config()
        
        return {
            "application": "简化 LangGraph 研究助手",
            "model": openai_config['model'],
            "document_count": len(self.workflow.documents) if self.workflow else 0,
            "status": "运行中"
        }


def main():
    """主函数"""
    try:
        # 创建应用
        app = SimpleLangGraphApp()
        
        # 显示状态
        status = app.get_status()
        print("\n" + "=" * 60)
        print("系统状态:")
        print("=" * 60)
        for key, value in status.items():
            print(f"{key}: {value}")
        
        # 设置文档
        print("\n" + "-" * 40)
        print("设置文档...")
        print("-" * 40)
        
        setup_result = app.setup_documents()
        print(f"状态: {setup_result['status']}")
        print(f"消息: {setup_result['message']}")
        
        if setup_result['status'] == 'success':
            # 测试查询
            print("\n" + "-" * 40)
            print("测试查询...")
            print("-" * 40)
            
            test_queries = [
                "什么是 LangGraph？",
                "LlamaIndex 的主要功能是什么？",
                "如何构建机器学习项目？",
                "Python 数据科学有哪些重要库？"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n查询 {i}: {query}")
                print("-" * 20)
                
                result = app.query(query)
                
                if result['status'] == 'success':
                    print(f"分析: {result['analysis'][:150]}...")
                    print(f"回答: {result['response'][:200]}...")
                    print(f"相关文档: {result['relevant_docs_count']} 个")
                    print(f"处理步骤: {result['step_count']}")
                else:
                    print(f"错误: {result['response']}")
        
        print("\n" + "=" * 60)
        print("演示完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        logger.error(f"运行失败: {str(e)}")
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
