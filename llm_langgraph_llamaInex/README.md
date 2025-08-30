# 智能研究助手 - LangGraph + LlamaIndex + OpenAI 集成案例

这是一个综合展示 LangGraph、LlamaIndex 和 OpenAI 强大功能的智能研究助手应用，支持多环境配置和企业级部署。

## ✨ 功能特性

- **🔍 智能文档问答**: 基于 GPT-4 的高质量问答体验
- **📚 多格式文档支持**: PDF、TXT、MD、DOCX 等格式
- **🧠 复杂推理工作流**: LangGraph 构建的多步推理流程
- **⚡ 高效向量检索**: LlamaIndex 实现毫秒级语义搜索
- **🌍 多环境支持**: 开发、测试、生产环境独立配置
- **🎨 现代化界面**: Streamlit 提供直观的 Web 界面
- **📊 实时监控**: 性能统计和使用分析
- **🛡️ 企业级安全**: 支持认证、HTTPS 和访问控制

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置设置
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，设置 OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动应用

#### Windows 用户 (推荐)
```powershell
# 开发环境启动
.\start.ps1

# 测试环境启动  
.\start.ps1 run -Environment staging

# 生产环境启动
.\start.ps1 run -Environment production
```

#### 跨平台启动
```bash
# 使用 Python 脚本
python start.py run --env development

# 直接使用 Streamlit
streamlit run streamlit_app.py --server.port 8501
```

## 🌍 多环境支持

| 环境 | 用途 | 模型 | 端口 | 特点 |
|------|------|------|------|------|
| **development** | 本地开发调试 | gpt-3.5-turbo | 8501 | 成本优化、详细日志 |
| **staging** | 功能测试验证 | gpt-4-turbo-preview | 8502 | 接近生产配置 |
| **production** | 正式部署使用 | gpt-4-turbo-preview | 8080 | 最佳性能、安全优化 |

详细配置说明请参考 [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

## 💡 使用方法

1. **文档上传**: 支持 PDF, TXT, MD, DOCX 格式
2. **智能问答**: 自然语言提问，多轮对话支持
3. **实时监控**: 置信度评估和性能统计
4. **导出功能**: 对话记录导出和分析

## 🔧 技术架构

### 核心技术栈
- **LangGraph**: 复杂推理工作流编排
- **LlamaIndex**: 文档索引和向量检索
- **OpenAI GPT-4**: 语言理解和生成
- **ChromaDB**: 向量数据库存储
- **Streamlit**: Web 界面框架
