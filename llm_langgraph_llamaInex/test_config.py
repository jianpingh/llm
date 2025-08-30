"""
环境配置测试脚本
用于测试不同环境配置的加载和验证
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from config import EnvironmentConfig


def test_environment(env_name: str):
    """测试指定环境配置"""
    print(f"\n{'='*50}")
    print(f"测试环境: {env_name}")
    print(f"{'='*50}")
    
    try:
        # 创建配置实例
        config = EnvironmentConfig(env_name)
        
        # 打印配置摘要
        config.print_config_summary()
        
        # 验证配置
        validation = config.validate_config()
        
        if validation['valid']:
            print(f"✅ 环境 {env_name} 配置验证通过!")
        else:
            print(f"❌ 环境 {env_name} 配置验证失败:")
            for issue in validation['issues']:
                print(f"   - {issue}")
        
        return validation['valid']
        
    except Exception as e:
        print(f"❌ 环境 {env_name} 配置加载失败: {e}")
        return False


def test_all_environments():
    """测试所有环境配置"""
    environments = ['development', 'staging', 'production']
    results = {}
    
    print("开始测试所有环境配置...")
    
    for env in environments:
        results[env] = test_environment(env)
    
    # 总结
    print(f"\n{'='*50}")
    print("测试总结")
    print(f"{'='*50}")
    
    for env, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{env:12}: {status}")
    
    total_passed = sum(results.values())
    print(f"\n总计: {total_passed}/{len(environments)} 个环境配置通过测试")
    
    return all(results.values())


def test_config_switching():
    """测试配置切换功能"""
    print(f"\n{'='*50}")
    print("测试配置切换功能")
    print(f"{'='*50}")
    
    try:
        from config import switch_environment, get_config
        
        # 初始配置
        initial_config = get_config()
        print(f"初始环境: {initial_config.environment}")
        
        # 切换到生产环境
        prod_config = switch_environment('production')
        print(f"切换后环境: {prod_config.environment}")
        
        # 验证全局配置已更新
        current_config = get_config()
        print(f"全局配置环境: {current_config.environment}")
        
        if current_config.environment == 'production':
            print("✅ 配置切换功能正常")
            return True
        else:
            print("❌ 配置切换功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 配置切换测试失败: {e}")
        return False


def create_test_env_file():
    """创建测试用的环境文件"""
    test_env_content = """# 测试环境配置
ENVIRONMENT=test
OPENAI_API_KEY=test_key_123
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHROMA_PERSIST_DIRECTORY=./indexes/test_chroma_db
DEBUG=true
LOG_LEVEL=DEBUG
"""
    
    with open('.env.test', 'w', encoding='utf-8') as f:
        f.write(test_env_content)
    
    print("✅ 测试环境文件已创建: .env.test")


def cleanup_test_files():
    """清理测试文件"""
    test_files = ['.env.test']
    
    for file_path in test_files:
        if Path(file_path).exists():
            Path(file_path).unlink()
            print(f"🗑️ 已删除测试文件: {file_path}")


def main():
    """主函数"""
    print("🚀 环境配置测试工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # 测试指定环境
        env_name = sys.argv[1]
        test_environment(env_name)
    else:
        # 测试所有功能
        print("1. 测试所有环境配置...")
        all_passed = test_all_environments()
        
        print("\n2. 测试配置切换功能...")
        switch_passed = test_config_switching()
        
        print("\n3. 创建测试环境文件...")
        create_test_env_file()
        test_env_passed = test_environment('test')
        
        print("\n4. 清理测试文件...")
        cleanup_test_files()
        
        # 最终结果
        print(f"\n{'='*50}")
        print("最终测试结果")
        print(f"{'='*50}")
        
        tests = [
            ("环境配置", all_passed),
            ("配置切换", switch_passed),
            ("测试环境", test_env_passed),
        ]
        
        for test_name, result in tests:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:12}: {status}")
        
        total_passed = sum(result for _, result in tests)
        print(f"\n总计: {total_passed}/{len(tests)} 项测试通过")
        
        if all(result for _, result in tests):
            print("\n🎉 所有测试通过! 环境配置系统工作正常。")
            sys.exit(0)
        else:
            print("\n💥 部分测试失败! 请检查配置文件。")
            sys.exit(1)


if __name__ == "__main__":
    main()
