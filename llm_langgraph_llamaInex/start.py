"""
智能研究助手启动脚本
支持多环境启动
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_streamlit(environment="development", port=None, host="localhost"):
    """运行 Streamlit 应用"""
    
    # 设置环境变量
    os.environ["ENVIRONMENT"] = environment
    
    # 根据环境设置默认端口
    if port is None:
        port_map = {
            "development": 8501,
            "staging": 8502,
            "production": 8080
        }
        port = port_map.get(environment, 8501)
    
    print(f"🚀 启动智能研究助手")
    print(f"环境: {environment}")
    print(f"地址: http://{host}:{port}")
    print(f"{'='*50}")
    
    # 构建启动命令
    cmd = [
        "streamlit", "run", "streamlit_app.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")


def test_config(environment=None):
    """测试配置"""
    if environment:
        cmd = ["python", "test_config.py", environment]
    else:
        cmd = ["python", "test_config.py"]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 配置测试失败: {e}")
        sys.exit(1)


def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖包...")
    
    cmd = ["pip", "install", "-r", "requirements.txt"]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        sys.exit(1)


def show_config(environment="development"):
    """显示配置信息"""
    os.environ["ENVIRONMENT"] = environment
    
    try:
        from config import EnvironmentConfig
        config = EnvironmentConfig(environment)
        config.print_config_summary()
    except Exception as e:
        print(f"❌ 显示配置失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能研究助手启动工具")
    parser.add_argument(
        "command",
        choices=["run", "test", "install", "config"],
        help="执行的命令"
    )
    parser.add_argument(
        "--env", "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="运行环境 (默认: development)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        help="端口号"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="主机地址 (默认: localhost)"
    )
    
    args = parser.parse_args()
    
    if args.command == "run":
        run_streamlit(args.env, args.port, args.host)
    elif args.command == "test":
        test_config(args.env if args.env != "development" else None)
    elif args.command == "install":
        install_dependencies()
    elif args.command == "config":
        show_config(args.env)


if __name__ == "__main__":
    main()
