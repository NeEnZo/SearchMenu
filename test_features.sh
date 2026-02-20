#!/bin/bash

# SearchMenu 功能测试脚本

echo "=================================="
echo "SearchMenu 功能测试"
echo "=================================="
echo ""

# 测试 1: 检查后端是否运行
echo "✓ 测试 1: 检查后端服务健康状态"
HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"ok"')
if [ -n "$HEALTH" ]; then
    echo "  ✅ 后端服务正常"
else
    echo "  ❌ 后端服务未运行或异常"
    exit 1
fi
echo ""

# 测试 2: 检查菜品总数
echo "✓ 测试 2: 检查菜品总数"
TOTAL=$(curl -s http://localhost:8000/api/v1/metadata | grep -o '"total_dishes":[0-9]*' | grep -o '[0-9]*')
echo "  📊 总菜品数：$TOTAL 个"
if [ "$TOTAL" -eq 342 ]; then
    echo "  ✅ 菜品数量正确（期望 342 个）"
else
    echo "  ⚠️  菜品数量异常（期望 342，实际 $TOTAL）"
fi
echo ""

# 测试 3: 搜索"番茄"
echo "✓ 测试 3: 搜索功能 - 搜索'番茄'"
TOMATO_COUNT=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E7%95%AA%E8%8C%84" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
echo "  🍅 搜索'番茄'返回：$TOMATO_COUNT 个结果"
if [ "$TOMATO_COUNT" -gt 0 ]; then
    echo "  ✅ 搜索功能正常"
else
    echo "  ❌ 搜索功能异常"
fi
echo ""

# 测试 4: 搜索"鸡蛋"
echo "✓ 测试 4: 搜索功能 - 搜索'鸡蛋'"
EGG_COUNT=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E9%B8%A1%E8%9B%8B" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
echo "  🥚 搜索'鸡蛋'返回：$EGG_COUNT 个结果"
if [ "$EGG_COUNT" -gt 0 ]; then
    echo "  ✅ 食材搜索功能正常"
else
    echo "  ❌ 食材搜索功能异常"
fi
echo ""

# 测试 5: 搜索"西红柿鸡蛋汤"
echo "✓ 测试 5: 搜索功能 - 搜索'西红柿鸡蛋汤'"
SOUP_COUNT=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E8%A5%BF%E7%BA%A2%E6%9F%BF%E9%B8%A1%E8%9B%8B" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
echo "  🍲 搜索'西红柿鸡蛋'返回：$SOUP_COUNT 个结果"
if [ "$SOUP_COUNT" -gt 0 ]; then
    echo "  ✅ 多条件搜索功能正常"
else
    echo "  ❌ 多条件搜索功能异常"
fi
echo ""

echo "=================================="
echo "测试完成！"
echo "=================================="
echo ""
echo "📝 访问前端应用："
echo "  🌐 http://localhost:5183"
echo ""
echo "🔍 API 文档："
echo "  📖 http://localhost:8000/docs"
echo ""
