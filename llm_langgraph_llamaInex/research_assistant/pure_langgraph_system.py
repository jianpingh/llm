"""
纯 LangGraph 实现的文档处理和检索系统
避免与 LlamaIndex 的版本冲突
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import pickle
from dataclasses import dataclass
import hashlib

# OpenAI相关
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """文档元数据"""
    filename: str
    file_type: str
    file_size: int
    created_at: str
    chunk_id: str
    source: str


class LangGraphDocumentProcessor:
    """基于 LangGraph 的文档处理器"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """初始化文档处理器"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.supported_types = ['.txt', '.md', '.html', '.py', '.js', '.json']
        logger.info(f"LangGraph 文档处理器初始化完成")
    
    def process_file(self, file_path: str) -> List[Document]:
        """处理单个文件"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return []
            
            if file_path.suffix.lower() not in self.supported_types:
                logger.warning(f"不支持的文件类型: {file_path.suffix}")
                return []
            
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        content = f.read()
                except:
                    logger.error(f"无法读取文件编码: {file_path}")
                    return []
            
            if not content.strip():
                logger.warning(f"文件内容为空: {file_path}")
                return []
            
            # 分割文档
            text_chunks = self.text_splitter.split_text(content)
            
            # 创建 Document 对象
            documents = []
            for i, chunk in enumerate(text_chunks):
                chunk_id = hashlib.md5(f"{file_path}_{i}".encode()).hexdigest()[:8]
                
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'filename': file_path.name,
                        'file_type': file_path.suffix[1:],
                        'file_size': file_path.stat().st_size,
                        'chunk_id': chunk_id,
                        'chunk_index': i,
                        'source': str(file_path),
                        'total_chunks': len(text_chunks)
                    }
                )
                documents.append(doc)
            
            logger.info(f"成功处理文件 {file_path.name}: {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {str(e)}")
            return []
    
    def process_directory(self, directory_path: str) -> List[Document]:
        """处理目录中的所有文件"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                logger.error(f"目录不存在: {directory_path}")
                return []
            
            all_documents = []
            processed_files = 0
            
            for file_path in directory_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_types:
                    documents = self.process_file(file_path)
                    if documents:
                        all_documents.extend(documents)
                        processed_files += 1
            
            logger.info(f"目录处理完成: 处理了 {processed_files} 个文件，生成 {len(all_documents)} 个文档块")
            return all_documents
            
        except Exception as e:
            logger.error(f"处理目录失败 {directory_path}: {str(e)}")
            return []


class LangGraphVectorStore:
    """基于 LangGraph 的向量存储"""
    
    def __init__(self, 
                 persist_directory: str = "./indexes/langgraph_vectorstore",
                 openai_api_key: str = None,
                 embedding_model: str = "text-embedding-ada-002"):
        """初始化向量存储"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API密钥未设置")
        
        # 初始化嵌入模型
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model=embedding_model
        )
        
        # 初始化向量存储
        self.vectorstore = None
        self.document_count = 0
        
        logger.info(f"LangGraph 向量存储初始化完成")
    
    def add_documents(self, documents: List[Document]) -> bool:
        """添加文档到向量存储"""
        try:
            if not documents:
                logger.warning("没有文档可以添加")
                return False
            
            logger.info(f"正在添加 {len(documents)} 个文档到向量存储...")
            
            if self.vectorstore is None:
                # 创建新的向量存储
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
            else:
                # 添加到现有向量存储
                self.vectorstore.add_documents(documents)
            
            # 持久化
            self.vectorstore.persist()
            self.document_count += len(documents)
            
            logger.info(f"成功添加 {len(documents)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            return False
    
    def load_vectorstore(self) -> bool:
        """加载现有向量存储"""
        try:
            if not self.persist_directory.exists():
                logger.info("向量存储目录不存在")
                return False
            
            # 检查是否有现有数据
            if not any(self.persist_directory.iterdir()):
                logger.info("向量存储目录为空")
                return False
            
            logger.info("加载现有向量存储...")
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            
            # 获取文档数量
            try:
                collection = self.vectorstore._collection
                self.document_count = collection.count()
                logger.info(f"成功加载向量存储，包含 {self.document_count} 个文档")
                return True
            except:
                logger.info("成功加载向量存储")
                return True
                
        except Exception as e:
            logger.error(f"加载向量存储失败: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """相似性搜索"""
        try:
            if self.vectorstore is None:
                logger.error("向量存储未初始化")
                return []
            
            # 执行相似性搜索
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # 格式化结果
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    'content': doc.page_content,
                    'score': 1.0 - score,  # Chroma返回距离，转换为相似度
                    'metadata': doc.metadata
                })
            
            logger.debug(f"相似性搜索返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"相似性搜索失败: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "document_count": self.document_count,
            "persist_directory": str(self.persist_directory),
            "status": "已初始化" if self.vectorstore is not None else "未初始化",
            "embedding_model": self.embeddings.model
        }


class LangGraphRAGSystem:
    """基于 LangGraph 的 RAG 系统"""
    
    def __init__(self, 
                 openai_api_key: str,
                 model_name: str = "gpt-3.5-turbo",
                 embedding_model: str = "text-embedding-ada-002",
                 persist_directory: str = "./indexes/langgraph_vectorstore"):
        """初始化 RAG 系统"""
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        
        # 初始化组件
        self.document_processor = LangGraphDocumentProcessor()
        self.vectorstore = LangGraphVectorStore(
            persist_directory=persist_directory,
            openai_api_key=openai_api_key,
            embedding_model=embedding_model
        )
        
        # 初始化语言模型
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model=model_name,
            temperature=0.1
        )
        
        logger.info("LangGraph RAG 系统初始化完成")
    
    def setup_documents(self, documents_dir: str) -> Dict[str, Any]:
        """设置文档"""
        try:
            # 尝试加载现有向量存储
            if self.vectorstore.load_vectorstore():
                logger.info("使用现有向量存储")
                return {
                    "status": "success",
                    "message": "使用现有向量存储",
                    "stats": self.vectorstore.get_stats()
                }
            
            # 处理文档
            logger.info(f"处理新文档: {documents_dir}")
            documents = self.document_processor.process_directory(documents_dir)
            
            if not documents:
                return {"status": "error", "message": "没有找到可处理的文档"}
            
            # 添加到向量存储
            if self.vectorstore.add_documents(documents):
                return {
                    "status": "success",
                    "message": f"成功处理 {len(documents)} 个文档块",
                    "stats": self.vectorstore.get_stats()
                }
            else:
                return {"status": "error", "message": "向量存储创建失败"}
                
        except Exception as e:
            logger.error(f"文档设置失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        return self.vectorstore.similarity_search(query, k=top_k)
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "system_type": "LangGraph RAG System",
            "model": self.model_name,
            "components": {
                "document_processor": {
                    "supported_types": self.document_processor.supported_types,
                    "chunk_size": self.document_processor.chunk_size
                },
                "vectorstore": self.vectorstore.get_stats(),
                "llm": {
                    "model": self.model_name,
                    "temperature": 0.1
                }
            }
        }
