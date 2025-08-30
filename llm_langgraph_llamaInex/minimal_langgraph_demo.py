"""
最简 LangGraph 风格的研究助手演示
使用原生 OpenAI API，避免所有版本冲突
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import json
import re
import time

# 使用原生 OpenAI 客户端
try:
    import openai
except ImportError:
    print("请安装 openai 包: pip install openai")
    sys.exit(1)

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


class DocumentLoader:
    """文档加载器"""
    
    def __init__(self):
        self.supported_extensions = ['.txt', '.md', '.py', '.js', '.html']
    
    def load_documents(self, directory: str) -> List[Dict[str, Any]]:
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
                        doc = {
                            'filename': file_path.name,
                            'path': str(file_path),
                            'content': content,
                            'size': len(content)
                        }
                        documents.append(doc)
                        logger.info(f"加载文档: {file_path.name} ({len(content)} 字符)")
                except Exception as e:
                    logger.warning(f"读取文件失败 {file_path}: {str(e)}")
        
        logger.info(f"共加载 {len(documents)} 个文档")
        return documents
    
    def _read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:3000]  # 限制长度
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                return content[:3000]
            except:
                return ""


class SimpleRetriever:
    """简单检索器"""
    
    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """检索相关文档"""
        if not self.documents:
            return []
        
        # 简单的关键词匹配
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_docs = []
        
        for doc in self.documents:
            content_words = set(re.findall(r'\w+', doc['content'].lower()))
            score = len(query_words.intersection(content_words))
            
            if score > 0:
                scored_docs.append((doc, score))
        
        # 排序并返回top_k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:top_k]]


class LangGraphWorkflow:
    """LangGraph 风格的工作流"""
    
    def __init__(self, api_key: str):
        # 设置OpenAI API密钥
        openai.api_key = api_key
        self.documents = []
        self.retriever = None
        
        logger.info("LangGraph 风格工作流初始化完成")
    
    def load_documents(self, directory: str) -> Dict[str, Any]:
        """加载文档 - 工作流节点1"""
        try:
            logger.info("执行节点: 文档加载")
            
            loader = DocumentLoader()
            self.documents = loader.load_documents(directory)
            self.retriever = SimpleRetriever(self.documents)
            
            return {
                "status": "success",
                "message": f"成功加载 {len(self.documents)} 个文档",
                "document_count": len(self.documents)
            }
        except Exception as e:
            logger.error(f"文档加载节点失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def retrieve_context(self, query: str) -> Dict[str, Any]:
        """检索上下文 - 工作流节点2"""
        try:
            logger.info("执行节点: 上下文检索")
            
            if not self.retriever:
                return {"relevant_docs": [], "context": ""}
            
            relevant_docs = self.retriever.retrieve(query, top_k=3)
            context = "\n\n".join([f"文档: {doc['filename']}\n内容: {doc['content'][:500]}..." 
                                  for doc in relevant_docs])
            
            logger.info(f"检索到 {len(relevant_docs)} 个相关文档")
            
            return {
                "relevant_docs": relevant_docs,
                "context": context,
                "doc_count": len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"上下文检索节点失败: {str(e)}")
            return {"relevant_docs": [], "context": "", "doc_count": 0}
    
    def analyze_query(self, query: str, context: str) -> Dict[str, Any]:
        """分析查询 - 工作流节点3"""
        try:
            logger.info("执行节点: 查询分析")
            
            prompt = f"""作为一个研究分析师，请分析以下查询：

用户查询: {query}

相关文档内容:
{context[:1500] if context else "无相关文档"}

请提供：
1. 查询意图分析
2. 关键信息要点
3. 回答思路

保持分析简洁清晰。"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            analysis = response.choices[0].message.content
            logger.info("查询分析完成")
            
            return {"analysis": analysis, "status": "success"}
            
        except Exception as e:
            logger.error(f"查询分析节点失败: {str(e)}")
            return {"analysis": f"分析失败: {str(e)}", "status": "error"}
    
    def generate_response(self, query: str, analysis: str, context: str) -> Dict[str, Any]:
        """生成回答 - 工作流节点4"""
        try:
            logger.info("执行节点: 回答生成")
            
            prompt = f"""基于分析结果和相关文档，为用户提供详细、准确的回答：

用户查询: {query}

分析结果: {analysis}

相关文档:
{context[:2000] if context else "无相关文档"}

请提供：
1. 直接回答用户问题
2. 详细解释和说明
3. 相关示例或建议
4. 总结要点

确保回答结构清晰、内容准确、有实用价值。"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            logger.info("回答生成完成")
            
            return {"response": answer, "status": "success"}
            
        except Exception as e:
            logger.error(f"回答生成节点失败: {str(e)}")
            return {"response": f"回答生成失败: {str(e)}", "status": "error"}
    
    def execute_workflow(self, query: str) -> Dict[str, Any]:
        """执行完整工作流"""
        try:
            logger.info(f"开始执行 LangGraph 工作流: {query}")
            
            workflow_state = {
                "query": query,
                "step_count": 0,
                "execution_time": time.time()
            }
            
            # 节点1: 检索上下文
            logger.info("步骤1: 检索相关上下文")
            context_result = self.retrieve_context(query)
            workflow_state["step_count"] += 1
            workflow_state["relevant_docs"] = context_result["relevant_docs"]
            workflow_state["context"] = context_result["context"]
            
            # 节点2: 分析查询
            logger.info("步骤2: 分析查询意图")  
            analysis_result = self.analyze_query(query, context_result["context"])
            workflow_state["step_count"] += 1
            workflow_state["analysis"] = analysis_result["analysis"]
            
            # 节点3: 生成回答
            logger.info("步骤3: 生成最终回答")
            response_result = self.generate_response(
                query, 
                analysis_result["analysis"], 
                context_result["context"]
            )
            workflow_state["step_count"] += 1
            workflow_state["response"] = response_result["response"]
            
            # 计算执行时间
            workflow_state["execution_time"] = time.time() - workflow_state["execution_time"]
            workflow_state["status"] = "success"
            
            logger.info("LangGraph 工作流执行完成")
            return workflow_state
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            return {
                "query": query,
                "response": f"工作流执行失败: {str(e)}",
                "step_count": 0,
                "status": "error"
            }


class MinimalLangGraphApp:
    """最简 LangGraph 风格应用"""
    
    def __init__(self):
        self.config = config
        self.workflow = None
        
        # 确保日志目录存在
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("=" * 60)
        logger.info("最简 LangGraph 研究助手启动")
        logger.info("=" * 60)
        
        self._initialize()
    
    def _initialize(self):
        """初始化应用"""
        try:
            logger.info("初始化 LangGraph 工作流...")
            
            # 获取OpenAI配置
            openai_config = self.config.get_openai_config()
            api_key = openai_config['api_key']
            
            if not api_key:
                raise ValueError("OpenAI API 密钥未配置")
            
            self.workflow = LangGraphWorkflow(api_key)
            logger.info("应用初始化完成")
            
        except Exception as e:
            logger.error(f"应用初始化失败: {str(e)}")
            raise
    
    def setup_documents(self, documents_dir: str = "./sample_documents") -> Dict[str, Any]:
        """设置文档"""
        return self.workflow.load_documents(documents_dir)
    
    def query(self, question: str) -> Dict[str, Any]:
        """处理查询"""
        return self.workflow.execute_workflow(question)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        openai_config = self.config.get_openai_config()
        
        return {
            "application": "最简 LangGraph 研究助手",
            "model": openai_config['model'],
            "document_count": len(self.workflow.documents) if self.workflow else 0,
            "environment": self.config.environment,
            "status": "运行中"
        }


def main():
    """主函数"""
    try:
        # 创建应用
        app = MinimalLangGraphApp()
        
        # 显示状态
        status = app.get_status()
        print("\n" + "=" * 60)
        print("🔬 LangGraph 研究助手状态")
        print("=" * 60)
        for key, value in status.items():
            print(f"{key}: {value}")
        
        # 设置文档
        print("\n" + "-" * 40)
        print("📚 设置文档库...")
        print("-" * 40)
        
        setup_result = app.setup_documents()
        print(f"状态: {setup_result['status']}")
        print(f"消息: {setup_result['message']}")
        
        if setup_result['status'] == 'success':
            # 测试查询
            print("\n" + "-" * 40)
            print("🧠 LangGraph 工作流测试")
            print("-" * 40)
            
            test_queries = [
                "什么是 LangGraph？它有什么特点？",
                "LlamaIndex 的主要功能是什么？",
                "如何构建一个机器学习项目？",
                "Python 数据科学有哪些重要工具？"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n🔍 查询 {i}: {query}")
                print("-" * 30)
                
                result = app.query(query)
                
                if result['status'] == 'success':
                    # 显示执行信息
                    print(f"⏱️ 执行时间: {result['execution_time']:.2f} 秒")
                    print(f"📊 处理步骤: {result['step_count']}")
                    print(f"📋 相关文档: {len(result.get('relevant_docs', []))} 个")
                    
                    # 显示分析
                    if 'analysis' in result:
                        analysis = result['analysis']
                        print(f"\n🎯 分析结果:")
                        if len(analysis) > 200:
                            print(f"{analysis[:200]}...")
                        else:
                            print(analysis)
                    
                    # 显示回答
                    response = result['response']
                    print(f"\n💡 回答:")
                    if len(response) > 300:
                        print(f"{response[:300]}...")
                    else:
                        print(response)
                        
                else:
                    print(f"❌ 错误: {result['response']}")
        
        print("\n" + "=" * 60)
        print("✅ LangGraph 演示完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    except Exception as e:
        logger.error(f"应用运行失败: {str(e)}")
        print(f"\n❌ 错误: {str(e)}")


if __name__ == "__main__":
    main()
