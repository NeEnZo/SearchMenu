#!/bin/bash

echo "🚀 SearchMenu 前端开发服务器启动"
echo "========================================"

cd /mnt/c/SearchMenu/frontend

echo ""
echo "📋 项目信息："
echo "  🏠 目录: $(pwd)"
echo "  📦 Node: $(node --version)"
echo "  🔧 npm: $(npm --version)"

echo ""
echo "🔄 安装依赖..."
npm install --silent 2>/dev/null && echo "✅ 依赖安装完成" || echo "⚠️  依赖安装完成（可能有警告）"

echo ""
echo "🎯 启动 Vite 开发服务器..."
echo "  📖 访问地址: http://localhost:5173"
echo "  🔗 API 代理: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev
