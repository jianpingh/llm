"""
智能研究助手 Streamlit Web 应用
提供友好的网页界面
"""

import os
import streamlit as st
import logging
from pathlib import Path
import time

from config import get_config, switch_environment

# 配置页面
st.set_page_config(
    page_title="智能研究助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化配置
if "config" not in st.session_state:
    st.session_state.config = get_config()

logger = logging.getLogger(__name__)


@st.cache_resource
def initialize_app():
    """初始化应用（缓存以避免重复初始化）"""
    try:
        from main import ResearchAssistantApp
        environment = st.session_state.get('selected_environment', None)
        return ResearchAssistantApp(environment)
    except Exception as e:
        st.error(f"应用初始化失败: {str(e)}")
        logger.error(f"应用初始化失败: {str(e)}", exc_info=True)
        return None


def initialize_knowledge_base(app, uploaded_files=None):
    """初始化知识库"""
    config = st.session_state.config
    doc_config = config.get_document_config()
    data_dir = doc_config['documents_dir']
    
    # 创建数据目录
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    
    # 处理上传的文件
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = Path(data_dir) / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"文件 {uploaded_file.name} 上传成功！")
    
    # 检查是否有文档
    if any(Path(data_dir).iterdir()):
        with st.spinner("正在构建知识库..."):
            app.initialize_knowledge_base(data_dir, force_rebuild=True)
        st.success("知识库构建完成！")
        return True
    else:
        st.warning("请先上传文档文件")
        return False


def main():
    """主函数"""
    st.title("🤖 智能研究助手")
    st.markdown("**基于 LangGraph + LlamaIndex + OpenAI 的智能文档问答系统**")
    
    # 侧边栏
    with st.sidebar:
        st.header("🌍 环境配置")
        
        # 环境选择
        current_env = st.session_state.config.environment
        environment = st.selectbox(
            "选择环境",
            ["development", "staging", "production"],
            index=["development", "staging", "production"].index(current_env),
            help="选择运行环境"
        )
        
        # 如果环境改变，重新加载配置
        if environment != current_env:
            st.session_state.config = switch_environment(environment)
            st.session_state.selected_environment = environment
            st.rerun()
        
        # 显示当前环境信息
        with st.expander("📊 当前环境信息"):
            config = st.session_state.config
            app_config = config.get_app_config()
            st.write(f"**环境**: {app_config['environment']}")
            st.write(f"**调试模式**: {app_config['debug']}")
            st.write(f"**日志级别**: {app_config['log_level']}")
            
            openai_config = config.get_openai_config()
            st.write(f"**模型**: {openai_config['model']}")
            st.write(f"**API Key**: {'已配置' if openai_config['api_key'] else '❌ 未配置'}")
        
        st.header("📚 文档管理")
        
        # 文件上传
        doc_config = st.session_state.config.get_document_config()
        uploaded_files = st.file_uploader(
            "上传文档",
            type=doc_config['supported_types'],
            accept_multiple_files=True,
            help=f"支持格式: {', '.join(doc_config['supported_types'])}"
        )
        
        st.header("🔑 API 配置")
        
        # API Key 配置
        current_api_key = st.session_state.config.get_openai_config()['api_key'] or ""
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=current_api_key,
            help="请输入您的 OpenAI API Key"
        )
        
        if api_key and api_key != current_api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("API Key 已更新")
        
        # 模型配置
        openai_config = st.session_state.config.get_openai_config()
        model_name = st.selectbox(
            "选择模型",
            ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            index=0 if openai_config['model'] == "gpt-4-turbo-preview" else 
                  (1 if openai_config['model'] == "gpt-4" else 2),
            help="选择要使用的 OpenAI 模型"
        )
        
        embedding_model = st.selectbox(
            "选择嵌入模型",
            ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
            index=0 if openai_config['embedding_model'] == "text-embedding-3-small" else
                  (1 if openai_config['embedding_model'] == "text-embedding-3-large" else 2),
            help="选择要使用的嵌入模型"
        )
        
        # 高级设置
        with st.expander("⚙️ 高级设置"):
            retrieval_config = st.session_state.config.get_retrieval_config()
            workflow_config = st.session_state.config.get_workflow_config()
            
            chunk_size = st.slider("文档块大小", 512, 2048, doc_config['chunk_size'])
            chunk_overlap = st.slider("块重叠大小", 50, 500, doc_config['chunk_overlap'])
            max_iterations = st.slider("最大迭代次数", 1, 5, workflow_config['max_iterations'])
            top_k = st.slider("检索文档数量", 3, 15, retrieval_config['top_k'])
            similarity_threshold = st.slider("相似度阈值", 0.0, 1.0, retrieval_config['similarity_threshold'], 0.1)
    
    # 主界面
    if not api_key:
        st.error("❌ 请在侧边栏配置 OpenAI API Key")
        return
    
    # 初始化应用
    app = initialize_app()
    if not app:
        return
    
    # 处理文件上传和知识库初始化
    if uploaded_files or st.button("🔄 重新构建知识库"):
        if initialize_knowledge_base(app, uploaded_files):
            st.rerun()
    
    # 检查知识库状态
    try:
        index_stats = app.index_manager.get_index_stats()
        if index_stats.get("document_count", 0) == 0:
            st.info("📋 请上传文档以开始使用智能问答功能")
            return
    except Exception as e:
        st.error(f"检查知识库状态失败: {str(e)}")
        return
    
    # 显示知识库统计
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 文档数量", index_stats.get("document_count", 0))
    with col2:
        st.metric("📊 索引状态", index_stats.get("status", "未知"))
    with col3:
        chat_stats = app.chat_interface.get_chat_statistics()
        st.metric("💬 对话轮次", chat_stats.get("total_messages", 0) // 2)
    with col4:
        st.metric("⏱️ 会话时长", chat_stats.get("session_duration", "0分钟"))
    
    # 聊天界面
    st.header("💬 智能问答")
    
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 显示助手回答的额外信息
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                with st.expander("📊 详细信息"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**置信度**: {metadata.get('confidence', 0):.1%}")
                        st.write(f"**策略**: {metadata.get('strategy', '未知')}")
                    with col2:
                        st.write(f"**检索文档**: {metadata.get('retrieved_docs_count', 0)} 个")
                        st.write(f"**迭代次数**: {metadata.get('iterations', 0)} 次")
    
    # 聊天输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成助手回答
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                response = app.chat_interface.chat(prompt)
            
            st.markdown(response["answer"])
            
            # 显示置信度指示器
            confidence = response.get("confidence", 0)
            if confidence > 0.7:
                st.success(f"置信度: {confidence:.1%} ✅")
            elif confidence > 0.4:
                st.warning(f"置信度: {confidence:.1%} ⚠️")
            else:
                st.error(f"置信度: {confidence:.1%} ❌")
            
            # 添加助手消息到历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "metadata": response
            })
    
    # 操作按钮
    st.header("🛠️ 操作")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🗑️ 清空对话"):
            st.session_state.messages = []
            app.chat_interface.clear_history()
            st.success("对话历史已清空")
            st.rerun()
    
    with col2:
        if st.button("📊 查看统计"):
            stats = app.chat_interface.get_chat_statistics()
            st.json(stats)
    
    with col3:
        if st.button("📥 导出对话"):
            if st.session_state.messages:
                conversation = app.chat_interface.export_conversation("text")
                st.download_button(
                    "下载对话记录",
                    conversation,
                    file_name=f"conversation_{app.chat_interface.session_id}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("暂无对话记录")
    
    with col4:
        if st.button("🔄 重置系统"):
            # 清除缓存和重新初始化
            st.cache_resource.clear()
            st.session_state.clear()
            st.success("系统已重置")
            st.rerun()
    
    # 示例问题
    with st.expander("💡 示例问题"):
        st.markdown("""
        **总结类问题**:
        - 请总结这些文档的主要内容
        - 概述文档中提到的主要观点
        
        **比较类问题**:
        - 比较文档中不同方法的优缺点
        - 对比各种解决方案的特点
        
        **方法类问题**:
        - 如何实现文档中提到的技术？
        - 具体的操作步骤是什么？
        
        **分析类问题**:
        - 为什么选择这种方法？
        - 这个问题的根本原因是什么？
        """)
    
    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🚀 Powered by <strong>LangGraph</strong> + <strong>LlamaIndex</strong> + <strong>OpenAI</strong></p>
            <p>智能研究助手 - 让文档问答更简单</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
