#!/bin/bash

# SearchMenu 后端快速启动脚本

echo "🚀 SearchMenu 后端启动程序"
echo "===================================="

# 检查是否在正确的目录
if [ ! -d "backend" ]; then
    echo "❌ 错误：请在项目根目录 (/mnt/c/SearchMenu) 运行此脚本"
    exit 1
fi

# 进入后端目录
cd backend

echo ""
echo "📋 检查环境..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行初始化脚本"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "✅ 虚拟环境已激活"

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -q "fastapi" && echo "✅ FastAPI 已安装" || (echo "❌ 缺少 FastAPI" && exit 1)

# 检查数据库
echo "💾 检查数据库..."
if [ -f "search_menu.db" ]; then
    echo "✅ 数据库文件存在"
else
    echo "⚠️  数据库文件不存在，初始化中..."
    python3 scripts/init_db.py
fi

echo ""
echo "🎯 启动后端服务..."
echo ""
echo "📖 API 文档：http://localhost:8000/docs"
echo "🔗 备用文档：http://localhost:8000/redoc"
echo "🏥 健康检查：http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python3 -m uvicorn app.main:app --reload --port 8000
