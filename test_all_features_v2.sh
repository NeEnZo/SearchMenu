#!/bin/bash

echo "🧪 SearchMenu 完整功能测试"
echo "========================================"
echo ""

# 测试1：搜索"鸡"（单字，应该只搜菜名）
echo "✓ 测试1：单字搜索 - 搜索'鸡'"
RESULT1=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E9%B8%A1" | python -c "import json,sys; print(json.load(sys.stdin)['total'])")
echo "  结果：$RESULT1 个菜品（菜名中含'鸡'）"
echo ""

# 测试2：搜索"鸡蛋"（多字，搜菜名+食材）
echo "✓ 测试2：多字搜索 - 搜索'鸡蛋'"  
RESULT2=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E9%B8%A1%E8%9B%8B" | python -c "import json,sys; print(json.load(sys.stdin)['total'])")
echo "  结果：$RESULT2 个菜品（菜名或食材中含'鸡蛋'）"
echo ""

# 测试3：搜索"番茄"
echo "✓ 测试3：多字搜索 - 搜索'番茄'"
RESULT3=$(curl -s "http://localhost:8000/api/v1/dishes/search?q=%E7%95%AA%E8%8C%84" | python -c "import json,sys; print(json.load(sys.stdin)['total'])")
echo "  结果：$RESULT3 个菜品"
echo ""

# 测试4：检查推荐排序（多食材优先）
echo "✓ 测试4：推荐排序 - '番茄'+'鸡蛋'"
echo "  发送推荐请求..."
RECOMMEND=$(curl -s -X POST "http://localhost:8000/api/v1/dishes/recommend" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["番茄", "鸡蛋"], "limit": 3}')
echo "  前3个推荐菜品（应该优先显示同时含两种食材的）："
echo "$RECOMMEND" | python -c "
import json, sys
data = json.load(sys.stdin)
for i, dish in enumerate(data[:3], 1):
    matched = len(dish.get('matched_ingredients', []))
    print(f'    {i}. {dish[\"name\"]} ({matched}个食材匹配)')
"
echo ""

# 测试5：检查菜品分类
echo "✓ 测试5：菜品分类"
curl -s "http://localhost:8000/api/v1/categories" | python -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  共{data['count']}个分类：\")
for cat in data['categories']:
    print(f\"    - {cat}\")
" | head -15
echo ""

echo "========================================"
echo "✅ 所有功能测试完成！"
echo ""
echo "前端应用地址："
echo "  🌐 http://localhost:5184"
echo ""
echo "API 文档："
echo "  📖 http://localhost:8000/docs"
