# 智能研究助手 - 多环境配置指南

## 概述

智能研究助手现在支持多环境配置，让您能够在不同的开发阶段使用不同的配置设置。

## 环境类型

### 1. 开发环境 (development)
- **用途**: 本地开发和调试
- **特点**: 
  - 使用 `gpt-3.5-turbo` 模型（成本较低）
  - 启用详细日志和调试信息
  - 较小的文件大小限制
  - 端口: 8501

### 2. 测试环境 (staging)
- **用途**: 功能测试和预发布验证
- **特点**:
  - 使用 `gpt-4-turbo-preview` 模型
  - 中等级别的限制设置
  - 启用缓存和性能监控
  - 端口: 8502

### 3. 生产环境 (production)
- **用途**: 正式部署和用户使用
- **特点**:
  - 使用最佳模型配置
  - 启用所有安全和性能优化
  - 支持 HTTPS 和认证
  - 端口: 8080

## 配置文件说明

### 主配置文件
- `.env` - 基础配置模板，包含所有可用配置项
- `.env.example` - 配置示例文件

### 环境特定配置
- `.env.development` - 开发环境配置
- `.env.staging` - 测试环境配置  
- `.env.production` - 生产环境配置

## 快速开始

### 1. 基础设置

```powershell
# 复制并编辑配置文件
cp .env.example .env

# 编辑 .env 文件，至少设置以下项目：
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 启动应用

#### 使用 PowerShell 脚本 (Windows 推荐)

```powershell
# 开发环境启动
.\start.ps1

# 测试环境启动
.\start.ps1 run -Environment staging

# 生产环境启动
.\start.ps1 run -Environment production

# 自定义端口
.\start.ps1 run -Port 8080
```

#### 使用 Python 脚本

```bash
# 开发环境启动
python start.py run

# 测试环境启动
python start.py run --env staging

# 生产环境启动
python start.py run --env production
```

### 3. 配置测试

```powershell
# 测试所有环境配置
.\start.ps1 test

# 测试特定环境
.\start.ps1 test -Environment production
```

### 4. 安装依赖

```powershell
# 安装所需依赖包
.\start.ps1 install
```

## 配置项详解

### OpenAI 配置
```bash
# 主要配置
OPENAI_API_KEY=your_api_key_here           # OpenAI API 密钥
OPENAI_MODEL=gpt-4-turbo-preview           # 主要对话模型
EMBEDDING_MODEL=text-embedding-3-small     # 嵌入模型

# 备用配置
OPENAI_API_KEY_BACKUP=backup_key_here      # 备用 API 密钥
OPENAI_MODEL_BACKUP=gpt-3.5-turbo          # 备用模型

# Azure OpenAI (可选)
USE_AZURE_OPENAI=false                     # 是否使用 Azure
AZURE_OPENAI_API_KEY=azure_key_here        # Azure API 密钥
AZURE_OPENAI_ENDPOINT=https://your-endpoint/  # Azure 端点
```

### 应用配置
```bash
ENVIRONMENT=development                     # 环境类型
DEBUG=true                                 # 调试模式
LOG_LEVEL=INFO                            # 日志级别
APP_NAME=智能研究助手                        # 应用名称
```

### 文档处理配置
```bash
DEFAULT_CHUNK_SIZE=1024                    # 文档块大小
DEFAULT_CHUNK_OVERLAP=200                  # 块重叠大小
SUPPORTED_FILE_TYPES=pdf,txt,md,docx      # 支持的文件类型
MAX_FILE_SIZE_MB=50                        # 最大文件大小
```

### 向量数据库配置
```bash
VECTOR_DB_TYPE=chroma                      # 数据库类型
CHROMA_PERSIST_DIRECTORY=./indexes/chroma_db  # ChromaDB 目录

# Pinecone 配置 (可选)
PINECONE_API_KEY=pinecone_key_here
PINECONE_ENVIRONMENT=your_env_here
PINECONE_INDEX_NAME=research-assistant
```

### 性能配置
```bash
RETRIEVAL_TOP_K=5                          # 检索文档数量
SIMILARITY_THRESHOLD=0.7                   # 相似度阈值
MAX_WORKFLOW_ITERATIONS=5                  # 最大工作流迭代
API_RATE_LIMIT=60                          # API 限制 (每分钟)
```

## 环境切换

### 在代码中切换环境
```python
from config import switch_environment, get_config

# 切换到生产环境
config = switch_environment('production')

# 获取当前配置
current_config = get_config()
```

### 在 Streamlit 应用中切换
应用界面左侧栏提供环境选择器，可以实时切换环境并查看配置差异。

## 配置验证

### 自动验证
应用启动时会自动验证配置，检查：
- 必需的 API 密钥是否存在
- 目录权限是否正确
- 数据库配置是否有效

### 手动验证
```powershell
# 验证所有环境
python test_config.py

# 验证特定环境
python test_config.py staging
```

## 最佳实践

### 1. 安全性
- 永远不要提交包含真实 API 密钥的 `.env` 文件
- 在生产环境中启用认证和 HTTPS
- 定期轮换 API 密钥

### 2. 性能优化
- 开发环境使用较小的模型以节省成本
- 生产环境启用缓存和性能监控
- 根据使用量调整 API 限制

### 3. 维护性
- 定期更新配置文档
- 为新环境创建专门的配置文件
- 使用配置验证确保设置正确

## 故障排除

### 常见问题

1. **API 密钥错误**
   ```
   解决方案: 检查 .env 文件中的 OPENAI_API_KEY 设置
   ```

2. **端口占用**
   ```
   解决方案: 使用 -Port 参数指定其他端口
   ```

3. **配置验证失败**
   ```
   解决方案: 运行 python test_config.py 查看具体错误
   ```

4. **模块导入错误**
   ```
   解决方案: 运行 .\start.ps1 install 安装依赖
   ```

### 调试技巧

1. **查看详细日志**
   ```bash
   # 设置调试级别
   LOG_LEVEL=DEBUG
   ```

2. **检查配置加载**
   ```python
   from config import get_config
   config = get_config()
   config.print_config_summary()
   ```

3. **验证环境变量**
   ```powershell
   # 在 PowerShell 中查看环境变量
   Get-ChildItem Env: | Where-Object Name -like "*OPENAI*"
   ```

## 自定义配置

### 添加新环境

1. 创建新的配置文件 `.env.new_environment`
2. 在启动脚本中添加新环境选项
3. 测试配置有效性

### 添加新配置项

1. 在 `.env` 中添加新配置项
2. 在 `config.py` 中添加相应的获取方法
3. 在应用代码中使用新配置

## 联系支持

如果您遇到配置问题，请：
1. 查看日志文件获取详细错误信息
2. 运行配置测试确认问题范围
3. 检查本文档的故障排除部分
