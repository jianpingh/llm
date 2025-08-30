"""
最简 LangGraph 风格的 Streamlit 应用
与 minimal_langgraph_demo.py 集成
"""

import streamlit as st
import sys
import logging
from pathlib import Path
import time
import uuid

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入主应用
from minimal_langgraph_demo import MinimalLangGraphApp

# 配置页面
st.set_page_config(
    page_title="🔬 LangGraph 研究助手",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_session_state():
    """初始化会话状态"""
    if 'app' not in st.session_state:
        st.session_state.app = None
    if 'documents_loaded' not in st.session_state:
        st.session_state.documents_loaded = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


@st.cache_resource
def load_app():
    """加载应用实例（使用缓存）"""
    try:
        with st.spinner('🚀 正在初始化 LangGraph 研究助手...'):
            app = MinimalLangGraphApp()
            return app, True, "应用初始化成功"
    except Exception as e:
        logger.error(f"应用初始化失败: {str(e)}")
        return None, False, f"初始化失败: {str(e)}"


def setup_documents(app):
    """设置文档"""
    try:
        with st.spinner('📚 正在加载文档库...'):
            result = app.setup_documents()
            return result['status'] == 'success', result['message']
    except Exception as e:
        return False, f"文档设置失败: {str(e)}"


def display_system_status(app):
    """显示系统状态"""
    with st.expander("🔧 系统状态", expanded=False):
        try:
            status = app.get_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 应用信息")
                st.write(f"**名称**: {status['application']}")
                st.write(f"**状态**: {status['status']}")
                st.write(f"**环境**: {status['environment']}")
                st.write(f"**模型**: {status['model']}")
            
            with col2:
                st.subheader("📚 文档信息")
                st.write(f"**文档数量**: {status['document_count']} 个")
                st.write(f"**会话ID**: {st.session_state.session_id}")
                st.write(f"**对话轮次**: {len(st.session_state.chat_history) // 2}")
                
        except Exception as e:
            st.error(f"获取系统状态失败: {str(e)}")


def display_workflow_demo():
    """显示工作流演示"""
    with st.expander("🔄 LangGraph 工作流演示", expanded=False):
        st.subheader("工作流步骤")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **步骤 1: 上下文检索**
            - 分析用户查询
            - 在文档库中搜索相关内容
            - 使用关键词匹配算法
            - 返回最相关的文档片段
            """)
        
        with col2:
            st.markdown("""
            **步骤 2: 查询分析**
            - 理解用户意图
            - 分析关键信息要点
            - 制定回答策略
            - 结合上下文信息
            """)
        
        with col3:
            st.markdown("""
            **步骤 3: 回答生成**
            - 基于分析结果生成回答
            - 结合相关文档内容
            - 提供详细解释和示例
            - 确保回答准确有用
            """)
        
        st.info("💡 每个步骤都会显示执行时间和处理结果，让您了解 LangGraph 工作流的运行过程。")


def display_chat_interface(app):
    """显示聊天界面"""
    st.subheader("💬 LangGraph 智能对话")
    
    # 聊天历史容器
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    
                    # 显示详细信息
                    if 'details' in message:
                        details = message['details']
                        
                        with st.expander("📋 详细执行信息", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("⏱️ 执行时间", f"{details.get('execution_time', 0):.2f} 秒")
                                st.metric("📊 处理步骤", details.get('step_count', 0))
                            
                            with col2:
                                st.metric("📋 相关文档", len(details.get('relevant_docs', [])))
                                st.metric("📄 状态", details.get('status', 'unknown'))
                            
                            with col3:
                                if 'context' in details:
                                    context_length = len(details['context'])
                                    st.metric("📝 上下文长度", f"{context_length} 字符")
                            
                            # 显示分析结果
                            if 'analysis' in details and details['analysis']:
                                st.subheader("🎯 查询分析")
                                with st.container():
                                    st.write(details['analysis'])
                            
                            # 显示相关文档
                            if 'relevant_docs' in details and details['relevant_docs']:
                                st.subheader("📚 相关文档")
                                for j, doc in enumerate(details['relevant_docs'][:2], 1):
                                    with st.expander(f"文档 {j}: {doc['filename']}"):
                                        st.write(f"**大小**: {doc['size']} 字符")
                                        st.write(f"**内容预览**:")
                                        st.code(doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content'])
    
    # 输入区域
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "请输入您的问题：",
                placeholder="例如：什么是LangGraph？Python数据科学有哪些重要工具？",
                key="user_input"
            )
        
        with col2:
            submit = st.form_submit_button("🚀 发送", use_container_width=True)
    
    if submit and user_input.strip():
        # 添加用户消息到历史
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # 显示处理状态
        with st.spinner('🧠 LangGraph 工作流正在处理您的问题...'):
            try:
                # 使用应用处理查询
                result = app.query(user_input)
                
                # 添加助手回复到历史
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'details': result
                })
                
                # 重新运行以更新界面
                st.rerun()
                
            except Exception as e:
                st.error(f"处理问题时出错: {str(e)}")


def main():
    """主函数"""
    st.title("🔬 LangGraph 研究助手")
    st.markdown("---")
    
    # 初始化会话状态
    initialize_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 初始化应用
        if st.session_state.app is None:
            if st.button("🚀 初始化应用", use_container_width=True):
                app, success, message = load_app()
                if success:
                    st.session_state.app = app
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        # 应用已初始化
        if st.session_state.app is not None:
            st.success("✅ 应用已初始化")
            
            # 文档设置
            st.subheader("📚 文档管理")
            
            if not st.session_state.documents_loaded:
                if st.button("📥 加载示例文档", use_container_width=True):
                    success, message = setup_documents(st.session_state.app)
                    
                    if success:
                        st.session_state.documents_loaded = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.success("✅ 文档已加载")
                
                if st.button("🔄 重新加载文档", use_container_width=True):
                    st.session_state.documents_loaded = False
                    st.rerun()
            
            # 聊天控制
            st.subheader("💬 对话管理")
            
            if st.button("🗑️ 清空对话历史", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()
            
            # 显示统计
            chat_count = len(st.session_state.chat_history)
            st.write(f"💬 对话轮次: {chat_count // 2}")
            
            # 预设问题
            st.subheader("❓ 快速问题")
            
            quick_questions = [
                "什么是 LangGraph？",
                "LlamaIndex 的功能",
                "Python 数据科学工具",
                "机器学习项目流程"
            ]
            
            for question in quick_questions:
                if st.button(question, use_container_width=True):
                    # 模拟用户输入
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': question
                    })
                    
                    # 处理查询
                    with st.spinner('处理中...'):
                        result = st.session_state.app.query(question)
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': result['response'],
                            'details': result
                        })
                    
                    st.rerun()
    
    # 主内容区域
    if st.session_state.app is None:
        st.info("👈 请先在侧边栏初始化应用")
        
        # 显示功能介绍
        st.subheader("🎯 LangGraph 研究助手特点")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔄 LangGraph 工作流**
            - 多步骤智能处理流程
            - 上下文检索 → 查询分析 → 回答生成
            - 实时执行状态监控
            - 详细的处理过程展示
            """)
            
            st.markdown("""
            **📚 文档智能检索**
            - 支持多种文档格式
            - 关键词匹配算法
            - 相关性评分排序
            - 上下文感知搜索
            """)
        
        with col2:
            st.markdown("""
            **🧠 OpenAI GPT 驱动**
            - GPT-3.5-turbo 模型
            - 智能查询分析
            - 上下文感知回答
            - 结构化内容生成
            """)
            
            st.markdown("""
            **💡 交互式界面**
            - 实时对话体验
            - 详细执行信息展示
            - 文档来源追踪
            - 快速问题模板
            """)
        
        # 显示工作流演示
        display_workflow_demo()
    
    elif not st.session_state.documents_loaded:
        st.info("👈 请先在侧边栏加载文档")
        
        # 显示系统状态
        display_system_status(st.session_state.app)
        display_workflow_demo()
        
    else:
        # 显示聊天界面
        display_chat_interface(st.session_state.app)
        
        # 底部显示系统信息
        st.markdown("---")
        display_system_status(st.session_state.app)


if __name__ == "__main__":
    main()
