#!/bin/bash

# 测试脚本：验证所有修复

echo "=========================================="
echo "🧪 开始测试所有修复"
echo "=========================================="
echo ""

# 测试1: 菜品详情显示（应该过滤掉無效步骤和量词）
echo "📋 测试1: 菜品详情显示"
echo "获取随机菜品，检查步骤和食材量..."
random_dish=$(curl -s "http://localhost:8000/api/v1/dishes/random")
echo "菜品名称: $(echo "$random_dish" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])" 2>/dev/null || echo '获取失败')"

# 检查是否有步骤信息
step_count=$(echo "$random_dish" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('steps', [])))" 2>/dev/null || echo "0")
echo "  - 步骤数: $step_count"

# 检查食材量是否包含"適量"等无效词
ingredients=$(echo "$random_dish" | python3 -c "import sys, json; d=json.load(sys.stdin); print('; '.join([i['ingredient_name'] + ':' + i['quantity'] for i in d.get('ingredients', [])]))" 2>/dev/null)
echo "  - 食材: $ingredients"
echo ""

# 测试2: 推荐排序
echo "🔍 测试2: 推荐排序（番茄+鸡蛋）"
echo "调用推荐API，查看返回的菜品及其匹配食材数..."
recommendations=$(curl -s -X POST "http://localhost:8000/api/v1/dishes/recommend" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["番茄", "鸡蛋"], "limit": 15}')

echo "$recommendations" | python3 << 'EOF' 2>/dev/null || echo "JSON解析失败"
import sys, json
data = json.load(sys.stdin)
print(f"  总推荐数: {len(data)}")
print("")
print("  前12道菜品（按排序）:")
print("  序号 | 菜品名       | 匹配食材数 | 食材")
print("  ----|-------------|----------|----------------------------------")
for i, dish in enumerate(data[:12], 1):
    matched = dish.get('matched_ingredients', [])
    matched_count = len(matched)
    name = dish['name'][:10]
    ingredients_str = ', '.join(matched) if matched else '无'
    print(f"  {i:2d}  | {name:10s}  | {matched_count:9d} | {ingredients_str[:35]}")
EOF
echo ""

# 测试3: 验证前端是否有搜索框
echo "🔍 测试3: 验证前端结构"
echo "检查HTML中是否存在菜品搜索框..."
if grep -q 'id="search' /mnt/c/SearchMenu/frontend/index.html || \
   grep -q 'id="query' /mnt/c/SearchMenu/frontend/index.html || \
   grep -q 'type="search' /mnt/c/SearchMenu/frontend/index.html; then
  echo "  ✗ 发现搜索框相关元素"
else
  echo "  ✓ 未发现搜索框元素（已正确删除）"
fi

# 检查分类和难度过滤是否存在
if grep -q 'id="category-filter' /mnt/c/SearchMenu/frontend/index.html && \
   grep -q 'id="difficulty-filter' /mnt/c/SearchMenu/frontend/index.html; then
  echo "  ✓ 分类和难度过滤器存在"
else
  echo "  ✗ 分类或难度过滤器不存在"
fi

# 检查食材推荐是否存在
if grep -q 'id="ingredient-input' /mnt/c/SearchMenu/frontend/index.html; then
  echo "  ✓ 食材推荐输入框存在"
else
  echo "  ✗ 食材推荐输入框不存在"
fi

echo ""
echo "=========================================="
echo "✅ 测试完成！"
echo "=========================================="
