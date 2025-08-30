"""
LangGraph + LlamaIndex 集成的 Streamlit 应用
提供交互式研究助手界面
"""

import streamlit as st
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List
import uuid

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入应用组件
from langgraph_main import LangGraphResearchApp

# 配置页面
st.set_page_config(
    page_title="LangGraph + LlamaIndex 研究助手",
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
    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())


@st.cache_resource
def load_app():
    """加载应用实例（使用缓存）"""
    try:
        with st.spinner('正在初始化 LangGraph + LlamaIndex 研究助手...'):
            app = LangGraphResearchApp()
            return app, True, "应用初始化成功"
    except Exception as e:
        logger.error(f"应用初始化失败: {str(e)}")
        return None, False, f"初始化失败: {str(e)}"


def setup_documents(app, progress_bar):
    """设置文档"""
    try:
        progress_bar.progress(0.2, "正在处理文档...")
        result = app.setup_documents()
        
        if result['status'] == 'success':
            progress_bar.progress(1.0, "文档处理完成")
            return True, result['message']
        else:
            return False, result['message']
            
    except Exception as e:
        return False, f"文档设置失败: {str(e)}"


def display_system_status(app):
    """显示系统状态"""
    with st.expander("🔧 系统状态", expanded=False):
        try:
            status = app.get_system_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("应用信息")
                st.write(f"**状态**: {status['status']}")
                st.write(f"**环境**: {status['configuration']['environment']}")
                st.write(f"**模型**: {status['configuration']['model']}")
                st.write(f"**嵌入模型**: {status['configuration']['embedding_model']}")
            
            with col2:
                st.subheader("组件状态")
                components = status['components']
                
                # 文档处理器状态
                doc_status = components['document_processor']['status']
                st.write(f"**文档处理器**: {doc_status}")
                
                # 索引管理器状态
                index_status = components['index_manager']['status']
                st.write(f"**索引管理器**: {index_status}")
                
                # 工作流状态
                workflow_status = components['workflow']['status']
                st.write(f"**LangGraph 工作流**: {workflow_status}")
                
                # 索引统计
                if 'stats' in components['index_manager']:
                    stats = components['index_manager']['stats']
                    if 'document_count' in stats:
                        st.write(f"**文档数量**: {stats['document_count']}")
                
        except Exception as e:
            st.error(f"获取系统状态失败: {str(e)}")


def display_workflow_info(app):
    """显示工作流信息"""
    with st.expander("🔄 LangGraph 工作流信息", expanded=False):
        try:
            if app.workflow:
                info = app.workflow.get_workflow_info()
                
                st.subheader("工作流配置")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**类型**: {info['workflow_type']}")
                    st.write(f"**模型**: {info['model']}")
                    st.write(f"**温度**: {info['temperature']}")
                
                with col2:
                    st.write(f"**最大步骤**: {info['max_steps']}")
                    st.write(f"**启用内存**: {info['enable_memory']}")
                    st.write(f"**状态**: {info['status']}")
                
                st.subheader("工作流节点")
                for i, node in enumerate(info['nodes'], 1):
                    st.write(f"{i}. {node}")
            else:
                st.warning("工作流未初始化")
                
        except Exception as e:
            st.error(f"获取工作流信息失败: {str(e)}")


def display_chat_interface(app):
    """显示聊天界面"""
    st.subheader("💬 研究助手对话")
    
    # 聊天历史
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
                        
                        with st.expander("详细信息", expanded=False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if 'step_count' in details:
                                    st.write(f"**处理步骤**: {details['step_count']}")
                                if 'metadata' in details and 'quality_score' in details['metadata']:
                                    quality = details['metadata']['quality_score']
                                    st.write(f"**质量分数**: {quality:.2f}")
                            
                            with col2:
                                if 'sources' in details:
                                    st.write(f"**相关来源**: {len(details['sources'])} 个")
                            
                            # 显示分析结果
                            if 'analysis' in details and details['analysis']:
                                st.subheader("分析结果")
                                st.write(details['analysis'])
                            
                            # 显示来源
                            if 'sources' in details and details['sources']:
                                st.subheader("相关来源")
                                for j, source in enumerate(details['sources'][:3], 1):
                                    with st.expander(f"来源 {j} (相似度: {source.get('score', 0):.3f})"):
                                        st.write(source['content'])
    
    # 输入区域
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "请输入您的问题：",
                placeholder="例如：什么是LangGraph？它与LlamaIndex如何配合使用？",
                key="user_input"
            )
        
        with col2:
            submit = st.form_submit_button("发送", use_container_width=True)
    
    if submit and user_input.strip():
        # 添加用户消息到历史
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })
        
        # 显示处理状态
        with st.spinner('LangGraph 工作流正在处理您的问题...'):
            try:
                # 使用应用处理查询
                result = app.query(user_input, thread_id=st.session_state.thread_id)
                
                # 添加助手回复到历史
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['response'],
                    'details': {
                        'step_count': result.get('step_count', 0),
                        'sources': result.get('sources', []),
                        'analysis': result.get('analysis', ''),
                        'metadata': result.get('metadata', {})
                    }
                })
                
                # 重新运行以更新界面
                st.rerun()
                
            except Exception as e:
                st.error(f"处理问题时出错: {str(e)}")


def main():
    """主函数"""
    st.title("🔬 LangGraph + LlamaIndex 研究助手")
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
                    progress_bar = st.progress(0, "准备处理文档...")
                    success, message = setup_documents(st.session_state.app, progress_bar)
                    
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
                st.session_state.thread_id = str(uuid.uuid4())
                st.rerun()
            
            # 显示对话数量
            chat_count = len(st.session_state.chat_history)
            st.write(f"对话轮次: {chat_count // 2}")
    
    # 主内容区域
    if st.session_state.app is None:
        st.info("👈 请先在侧边栏初始化应用")
        
        # 显示功能介绍
        st.subheader("🎯 功能特点")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🔄 LangGraph 工作流**
            - 复杂推理流程管理
            - 多步骤查询分析
            - 智能响应生成
            - 质量验证机制
            """)
            
            st.markdown("""
            **📊 LlamaIndex 集成**
            - 高效文档索引
            - 语义向量搜索
            - 多格式文档支持
            - 智能上下文检索
            """)
        
        with col2:
            st.markdown("""
            **🧠 OpenAI 驱动**
            - GPT 模型推理
            - 智能嵌入生成
            - 自然语言理解
            - 上下文感知回答
            """)
            
            st.markdown("""
            **💡 其他特性**
            - 多环境配置
            - 实时对话界面
            - 工作流状态监控
            - 详细来源追踪
            """)
    
    elif not st.session_state.documents_loaded:
        st.info("👈 请先在侧边栏加载文档")
        
        # 显示系统状态
        display_system_status(st.session_state.app)
        display_workflow_info(st.session_state.app)
        
    else:
        # 显示聊天界面
        display_chat_interface(st.session_state.app)
        
        # 底部显示系统信息
        st.markdown("---")
        display_system_status(st.session_state.app)
        display_workflow_info(st.session_state.app)


if __name__ == "__main__":
    main()
