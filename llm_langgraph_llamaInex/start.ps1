# 智能研究助手 PowerShell 启动脚本

param(
    [Parameter(Position=0)]
    [ValidateSet("run", "test", "install", "config")]
    [string]$Command = "run",
    
    [Parameter()]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter()]
    [int]$Port,
    
    [Parameter()]
    [string]$HostAddress = "localhost"
)

# 设置控制台输出编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    try {
        $colorMap = @{
            "Red" = [ConsoleColor]::Red
            "Green" = [ConsoleColor]::Green
            "Yellow" = [ConsoleColor]::Yellow
            "Blue" = [ConsoleColor]::Blue
            "Cyan" = [ConsoleColor]::Cyan
            "White" = [ConsoleColor]::White
        }
        
        if ($colorMap.ContainsKey($Color)) {
            Write-Host $Message -ForegroundColor $colorMap[$Color]
        } else {
            Write-Host $Message
        }
    }
    catch {
        Write-Host $Message
    }
}

# 检查 Python 环境
function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        Write-ColorOutput "✅ Python 环境: $pythonVersion" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "❌ 未找到 Python 环境，请先安装 Python" "Red"
        return $false
    }
}

# 检查必要的包
function Test-RequiredPackages {
    $requiredPackages = @("streamlit", "openai", "langchain", "llama-index")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            python -c "import $($package.Replace('-', '_'))" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        }
        catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-ColorOutput "⚠️ 缺少必要的包: $($missingPackages -join ', ')" "Yellow"
        Write-ColorOutput "请运行: .\start.ps1 install" "Yellow"
        return $false
    }
    
    Write-ColorOutput "✅ 所有必要的包已安装" "Green"
    return $true
}

# 运行应用
function Start-Application {
    Write-ColorOutput "🚀 启动智能研究助手" "Cyan"
    Write-ColorOutput "环境: $Environment" "White"
    
    # 设置默认端口
    if (-not $Port) {
        $portMap = @{
            "development" = 8501
            "staging" = 8502
            "production" = 8080
        }
        $Port = $portMap[$Environment]
    }
    
    Write-ColorOutput "地址: http://${HostAddress}:${Port}" "White"
    Write-ColorOutput "=" * 50 "White"
    
    # 设置环境变量
    $env:ENVIRONMENT = $Environment
    
    # 启动命令
    $arguments = @(
        "run", "streamlit_app.py",
        "--server.port", $Port,
        "--server.address", $HostAddress,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    )
    
    try {
        & streamlit @arguments
    }
    catch {
        Write-ColorOutput "❌ 启动失败: $_" "Red"
        exit 1
    }
}

# 测试配置
function Test-Configuration {
    Write-ColorOutput "🔧 测试配置..." "Cyan"
    
    $env:ENVIRONMENT = $Environment
    
    try {
        if ($Environment -eq "development") {
            python test_config.py
        } else {
            python test_config.py $Environment
        }
    }
    catch {
        Write-ColorOutput "❌ 配置测试失败: $_" "Red"
        exit 1
    }
}

# 安装依赖
function Install-Dependencies {
    Write-ColorOutput "📦 安装依赖包..." "Cyan"
    
    if (-not (Test-Path "requirements.txt")) {
        Write-ColorOutput "❌ 未找到 requirements.txt 文件" "Red"
        exit 1
    }
    
    try {
        pip install -r requirements.txt
        Write-ColorOutput "✅ 依赖安装完成" "Green"
    }
    catch {
        Write-ColorOutput "❌ 依赖安装失败: $_" "Red"
        exit 1
    }
}

# 显示配置
function Show-Configuration {
    Write-ColorOutput "📋 显示配置信息..." "Cyan"
    
    $env:ENVIRONMENT = $Environment
    
    try {
        python start.py config --env $Environment
    }
    catch {
        Write-ColorOutput "❌ 显示配置失败: $_" "Red"
        exit 1
    }
}

# 主逻辑
function Main {
    Write-ColorOutput @"
🤖 智能研究助手启动工具
基于 LangGraph + LlamaIndex + OpenAI
"@ "Cyan"
    
    Write-ColorOutput "=" * 50 "White"
    
    # 检查 Python 环境
    if (-not (Test-PythonEnvironment)) {
        exit 1
    }
    
    # 根据命令执行相应操作
    switch ($Command) {
        "run" {
            if (Test-RequiredPackages) {
                Start-Application
            }
        }
        "test" {
            Test-Configuration
        }
        "install" {
            Install-Dependencies
        }
        "config" {
            Show-Configuration
        }
        default {
            Write-ColorOutput "❌ 未知命令: $Command" "Red"
            Write-ColorOutput "支持的命令: run, test, install, config" "Yellow"
            exit 1
        }
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput @"
智能研究助手启动工具

用法:
    .\start.ps1 [命令] [选项]

命令:
    run      启动应用 (默认)
    test     测试配置
    install  安装依赖
    config   显示配置

选项:
    -Environment  环境 (development, staging, production)
    -Port         端口号
    -Host         主机地址

示例:
    .\start.ps1                              # 开发环境启动
    .\start.ps1 run -Environment staging     # 测试环境启动
    .\start.ps1 run -Port 8080              # 指定端口启动
    .\start.ps1 test                        # 测试配置
    .\start.ps1 install                     # 安装依赖
    .\start.ps1 config -Environment production  # 显示生产环境配置

"@ "White"
}

# 如果请求帮助
if ($args -contains "-h" -or $args -contains "--help" -or $args -contains "help") {
    Show-Help
    exit 0
}

# 执行主函数
Main
