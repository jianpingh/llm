"""
智能研究助手演示脚本
展示 LangGraph + LlamaIndex + OpenAI 的集成功能
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from config import EnvironmentConfig


def demo_introduction():
    """演示介绍"""
    print("🤖 智能研究助手演示")
    print("=" * 50)
    print("这是一个综合展示 LangGraph、LlamaIndex 和 OpenAI 强大功能的案例")
    print()
    print("✨ 主要特性:")
    print("- 🧠 LangGraph: 复杂推理工作流编排")
    print("- 📚 LlamaIndex: 高效文档索引和检索")
    print("- 🤖 OpenAI GPT-4: 强大的语言理解和生成")
    print("- 🌍 多环境支持: 开发、测试、生产环境")
    print("- 🎨 现代界面: Streamlit Web 应用")
    print()


def demo_environment_config():
    """演示环境配置"""
    print("🌍 多环境配置演示")
    print("-" * 30)
    
    environments = ['development', 'staging', 'production']
    
    for i, env in enumerate(environments, 1):
        print(f"\n{i}. {env.upper()} 环境:")
        
        try:
            config = EnvironmentConfig(env)
            
            # 获取关键配置
            app_config = config.get_app_config()
            openai_config = config.get_openai_config()
            streamlit_config = config.get_streamlit_config()
            
            print(f"   模型: {openai_config['model']}")
            print(f"   端口: {streamlit_config['port']}")
            print(f"   调试: {app_config['debug']}")
            print(f"   日志: {app_config['log_level']}")
            
        except Exception as e:
            print(f"   ❌ 配置加载失败: {e}")


def demo_workflow_components():
    """演示工作流组件"""
    print("\n🧩 核心组件演示")
    print("-" * 30)
    
    components = [
        {
            "name": "文档处理器 (DocumentProcessor)",
            "description": "支持多种格式文档的智能解析和分块",
            "features": [
                "PDF, TXT, MD, DOCX 格式支持",
                "智能文档分块和重叠处理",
                "元数据提取和保留"
            ]
        },
        {
            "name": "索引管理器 (IndexManager)",
            "description": "基于 LlamaIndex 的向量索引管理",
            "features": [
                "ChromaDB 向量数据库集成",
                "高效的语义搜索",
                "持久化索引存储"
            ]
        },
        {
            "name": "工作流引擎 (ResearchWorkflow)",
            "description": "LangGraph 驱动的智能推理工作流",
            "features": [
                "多步推理链编排",
                "动态策略选择",
                "上下文感知处理"
            ]
        },
        {
            "name": "聊天界面 (ChatInterface)",
            "description": "用户友好的对话交互界面",
            "features": [
                "多轮对话支持",
                "实时置信度评估",
                "对话历史管理"
            ]
        }
    ]
    
    for i, component in enumerate(components, 1):
        print(f"\n{i}. {component['name']}")
        print(f"   📝 {component['description']}")
        for feature in component['features']:
            print(f"   ✅ {feature}")


def demo_use_cases():
    """演示使用场景"""
    print("\n💡 应用场景演示")
    print("-" * 30)
    
    use_cases = [
        {
            "scenario": "学术研究",
            "description": "研究论文智能问答和分析",
            "example": "请总结这些论文的主要贡献和创新点"
        },
        {
            "scenario": "企业文档管理",
            "description": "内部文档智能检索和知识提取",
            "example": "我们的产品规格中提到了哪些技术标准？"
        },
        {
            "scenario": "法律文档分析",
            "description": "合同条款智能解读和风险识别",
            "example": "这份合同中有哪些潜在的法律风险？"
        },
        {
            "scenario": "技术文档问答",
            "description": "API 文档和技术手册智能问答",
            "example": "如何使用这个 API 实现用户认证功能？"
        }
    ]
    
    for i, case in enumerate(use_cases, 1):
        print(f"\n{i}. {case['scenario']}")
        print(f"   📋 {case['description']}")
        print(f"   💬 示例: \"{case['example']}\"")


def demo_architecture():
    """演示技术架构"""
    print("\n🏗️ 技术架构演示")
    print("-" * 30)
    
    print("""
数据流架构:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  文档上传   │───▶│  文档处理    │───▶│ 向量化存储  │
└─────────────┘    └──────────────┘    └─────────────┘
       │                    │                   │
       ▼                    ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  用户提问   │───▶│ LangGraph    │◀───│ 向量检索    │
└─────────────┘    │   工作流     │    └─────────────┘
       │           └──────────────┘           │
       ▼                    │                 ▼
┌─────────────┐            ▼         ┌─────────────┐
│  智能回答   │◀───────────────────────│  GPT-4 推理 │
└─────────────┘                      └─────────────┘

技术栈组合:
• 前端界面: Streamlit (Python Web 框架)
• 工作流编排: LangGraph (复杂推理链)
• 文档索引: LlamaIndex (向量检索)
• 语言模型: OpenAI GPT-4 (理解生成)
• 向量数据库: ChromaDB (语义搜索)
• 配置管理: 多环境配置系统
    """)


def demo_performance_features():
    """演示性能特性"""
    print("\n⚡ 性能特性演示")
    print("-" * 30)
    
    features = [
        {
            "category": "缓存优化",
            "items": [
                "向量计算结果缓存",
                "模型响应缓存",
                "文档处理缓存"
            ]
        },
        {
            "category": "并发处理",
            "items": [
                "异步向量检索",
                "批量文档处理",
                "连接池管理"
            ]
        },
        {
            "category": "资源管理",
            "items": [
                "内存使用优化",
                "API 调用限制",
                "错误重试机制"
            ]
        },
        {
            "category": "监控分析",
            "items": [
                "实时性能监控",
                "使用统计分析",
                "错误日志跟踪"
            ]
        }
    ]
    
    for feature in features:
        print(f"\n📊 {feature['category']}:")
        for item in feature['items']:
            print(f"   ✅ {item}")


def demo_quick_start():
    """演示快速开始"""
    print("\n🚀 快速开始演示")
    print("-" * 30)
    
    steps = [
        "安装依赖: pip install -r requirements.txt",
        "配置 API: 在 .env 文件中设置 OPENAI_API_KEY",
        "启动应用: .\\start.ps1 (Windows) 或 python start.py run",
        "上传文档: 使用界面上传 PDF、TXT、MD 等文件",
        "开始问答: 在聊天界面中提出你的问题"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"\n{i}. {step}")
        time.sleep(0.5)  # 模拟演示效果


def main():
    """主演示函数"""
    demo_introduction()
    time.sleep(2)
    
    demo_environment_config()
    time.sleep(2)
    
    demo_workflow_components()
    time.sleep(2)
    
    demo_use_cases()
    time.sleep(2)
    
    demo_architecture()
    time.sleep(2)
    
    demo_performance_features()
    time.sleep(2)
    
    demo_quick_start()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成!")
    print()
    print("💡 现在您可以:")
    print("- 运行 python start.py run 启动应用")
    print("- 访问 http://localhost:8501 体验功能")
    print("- 查看 CONFIG_GUIDE.md 了解详细配置")
    print("- 参考 README.md 获取更多信息")
    print()
    print("🚀 让智能文档问答改变您的工作方式!")


if __name__ == "__main__":
    main()
