"""
环境配置管理器
支持多环境配置加载和管理
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """环境配置管理器"""
    
    def __init__(self, environment: Optional[str] = None):
        """
        初始化环境配置
        
        Args:
            environment: 环境名称 (development, staging, production)
        """
        self.environment = environment or os.getenv('ENVIRONMENT', 'development')
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        # 1. 加载基础配置
        base_env_file = find_dotenv('.env')
        if base_env_file:
            load_dotenv(base_env_file)
            logger.info(f"已加载基础配置: {base_env_file}")
        
        # 2. 加载环境特定配置
        env_file = f'.env.{self.environment}'
        if Path(env_file).exists():
            load_dotenv(env_file, override=True)
            logger.info(f"已加载环境配置: {env_file}")
        else:
            logger.warning(f"环境配置文件不存在: {env_file}")
        
        # 3. 缓存当前配置
        self._cache_config()
    
    def _cache_config(self):
        """缓存当前环境变量"""
        self.config = dict(os.environ)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        value = self.config.get(key, default)
        
        # 尝试转换数据类型
        if isinstance(value, str):
            # 布尔值转换
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            
            # 数字转换
            if value.isdigit():
                return int(value)
            
            # 浮点数转换
            try:
                if '.' in value:
                    return float(value)
            except ValueError:
                pass
        
        return value
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取 OpenAI 配置"""
        return {
            'api_key': self.get('OPENAI_API_KEY'),
            'api_base': self.get('OPENAI_API_BASE'),
            'organization': self.get('OPENAI_ORG_ID'),
            'model': self.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
            'embedding_model': self.get('EMBEDDING_MODEL', 'text-embedding-ada-002'),
            'backup_key': self.get('OPENAI_API_KEY_BACKUP'),
            'backup_model': self.get('OPENAI_MODEL_BACKUP', 'gpt-3.5-turbo'),
        }
    
    def get_azure_openai_config(self) -> Dict[str, Any]:
        """获取 Azure OpenAI 配置"""
        return {
            'use_azure': self.get('USE_AZURE_OPENAI', False),
            'api_key': self.get('AZURE_OPENAI_API_KEY'),
            'endpoint': self.get('AZURE_OPENAI_ENDPOINT'),
            'api_version': self.get('AZURE_OPENAI_API_VERSION'),
            'deployment_name': self.get('AZURE_OPENAI_DEPLOYMENT_NAME'),
            'embedding_deployment': self.get('AZURE_EMBEDDING_DEPLOYMENT_NAME'),
        }
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """获取向量数据库配置"""
        db_type = self.get('VECTOR_DB_TYPE', 'chroma')
        
        config = {
            'type': db_type,
        }
        
        if db_type == 'chroma':
            config.update({
                'persist_directory': self.get('CHROMA_PERSIST_DIRECTORY', './indexes/chroma_db'),
            })
        elif db_type == 'pinecone':
            config.update({
                'api_key': self.get('PINECONE_API_KEY'),
                'environment': self.get('PINECONE_ENVIRONMENT'),
                'index_name': self.get('PINECONE_INDEX_NAME', 'research-assistant'),
            })
        elif db_type == 'weaviate':
            config.update({
                'url': self.get('WEAVIATE_URL', 'http://localhost:8080'),
                'api_key': self.get('WEAVIATE_API_KEY'),
            })
        
        return config
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return {
            'name': self.get('APP_NAME', '智能研究助手'),
            'debug': self.get('DEBUG', False),
            'log_level': self.get('LOG_LEVEL', 'INFO'),
            'log_file': self.get('LOG_FILE', './logs/app.log'),
            'environment': self.environment,
        }
    
    def get_document_config(self) -> Dict[str, Any]:
        """获取文档处理配置"""
        return {
            'chunk_size': self.get('DEFAULT_CHUNK_SIZE', 1024),
            'chunk_overlap': self.get('DEFAULT_CHUNK_OVERLAP', 200),
            'supported_types': self.get('SUPPORTED_FILE_TYPES', 'pdf,txt,md').split(','),
            'max_file_size_mb': self.get('MAX_FILE_SIZE_MB', 50),
            'documents_dir': self.get('DOCUMENTS_DIR', './data'),
            'temp_dir': self.get('TEMP_DIR', './temp'),
        }
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """获取工作流配置"""
        return {
            'max_iterations': self.get('MAX_WORKFLOW_ITERATIONS', 5),
            'timeout': self.get('WORKFLOW_TIMEOUT', 300),
            'enable_cache': self.get('ENABLE_WORKFLOW_CACHE', True),
        }
    
    def get_retrieval_config(self) -> Dict[str, Any]:
        """获取检索配置"""
        return {
            'top_k': self.get('RETRIEVAL_TOP_K', 5),
            'similarity_threshold': self.get('SIMILARITY_THRESHOLD', 0.7),
            'enable_reranking': self.get('ENABLE_RERANKING', True),
            'rerank_model': self.get('RERANK_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2'),
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取 API 配置"""
        return {
            'rate_limit': self.get('API_RATE_LIMIT', 60),
            'max_concurrent': self.get('MAX_CONCURRENT_REQUESTS', 10),
            'timeout': self.get('REQUEST_TIMEOUT', 60),
            'max_retries': self.get('MAX_RETRIES', 3),
            'enable_auth': self.get('ENABLE_API_AUTH', False),
            'api_token': self.get('API_TOKEN'),
        }
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """获取 Streamlit 配置"""
        return {
            'port': self.get('STREAMLIT_PORT', 8501),
            'host': self.get('STREAMLIT_HOST', 'localhost'),
            'file_watcher': self.get('STREAMLIT_FILE_WATCHER', True),
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        cache_type = self.get('CACHE_TYPE', 'memory')
        
        config = {
            'enabled': self.get('ENABLE_CACHE', True),
            'type': cache_type,
            'ttl': self.get('CACHE_TTL', 3600),
        }
        
        if cache_type == 'redis':
            config.update({
                'redis_host': self.get('REDIS_HOST', 'localhost'),
                'redis_port': self.get('REDIS_PORT', 6379),
                'redis_password': self.get('REDIS_PASSWORD'),
                'redis_db': self.get('REDIS_DB', 0),
            })
        
        return config
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return {
            'secret_key': self.get('SECRET_KEY'),
            'enable_https': self.get('ENABLE_HTTPS', False),
            'ssl_cert_path': self.get('SSL_CERT_PATH'),
            'ssl_key_path': self.get('SSL_KEY_PATH'),
            'allowed_origins': self.get('ALLOWED_ORIGINS', '').split(','),
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """获取监控配置"""
        return {
            'enable_analytics': self.get('ENABLE_ANALYTICS', True),
            'enable_performance': self.get('ENABLE_PERFORMANCE_MONITORING', True),
            'analytics_file': self.get('ANALYTICS_FILE', './logs/analytics.json'),
            'enable_access_log': self.get('ENABLE_ACCESS_LOG', False),
            'access_log_path': self.get('ACCESS_LOG_PATH', './logs/access.log'),
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置"""
        issues = []
        
        # 检查必需的配置
        openai_config = self.get_openai_config()
        if not openai_config['api_key']:
            issues.append("缺少 OPENAI_API_KEY")
        
        # 检查目录权限
        doc_config = self.get_document_config()
        for dir_path in [doc_config['documents_dir'], doc_config['temp_dir']]:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"无法创建目录 {dir_path}: {e}")
        
        # 检查向量数据库配置
        vector_config = self.get_vector_db_config()
        if vector_config['type'] == 'pinecone' and not vector_config.get('api_key'):
            issues.append("使用 Pinecone 时缺少 PINECONE_API_KEY")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'environment': self.environment,
        }
    
    def print_config_summary(self):
        """打印配置摘要"""
        print(f"\n=== 环境配置摘要 ({self.environment}) ===")
        
        # 应用配置
        app_config = self.get_app_config()
        print(f"应用名称: {app_config['name']}")
        print(f"调试模式: {app_config['debug']}")
        print(f"日志级别: {app_config['log_level']}")
        
        # OpenAI 配置
        openai_config = self.get_openai_config()
        print(f"OpenAI 模型: {openai_config['model']}")
        print(f"嵌入模型: {openai_config['embedding_model']}")
        print(f"API Key: {'已配置' if openai_config['api_key'] else '未配置'}")
        
        # 向量数据库配置
        vector_config = self.get_vector_db_config()
        print(f"向量数据库: {vector_config['type']}")
        
        # Streamlit 配置
        streamlit_config = self.get_streamlit_config()
        print(f"Streamlit 端口: {streamlit_config['port']}")
        
        # 验证结果
        validation = self.validate_config()
        print(f"配置验证: {'通过' if validation['valid'] else '失败'}")
        if not validation['valid']:
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        print("=" * 40)


# 全局配置实例
config = EnvironmentConfig()


def get_config() -> EnvironmentConfig:
    """获取全局配置实例"""
    return config


def switch_environment(environment: str) -> EnvironmentConfig:
    """切换环境"""
    global config
    config = EnvironmentConfig(environment)
    return config


if __name__ == "__main__":
    # 测试配置加载
    import sys
    
    env = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    config = EnvironmentConfig(env)
    config.print_config_summary()
    
    # 验证配置
    validation = config.validate_config()
    if not validation['valid']:
        print(f"\n配置验证失败:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print(f"\n✅ 配置验证通过!")
