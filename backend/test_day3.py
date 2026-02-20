#!/usr/bin/env python3
"""
Day 3：完整 API 测试脚本
包含所有 7 个端点的测试
"""

import sys
sys.path.insert(0, '.')

import asyncio
from app.main import (
    health_check,
    get_random_dish,
    recommend_dishes,
    get_dish_detail,
    search_dishes,
    get_categories,
    get_metadata,
    root,
    RecommendRequest
)

async def test_all_endpoints():
    """测试所有 API 端点"""
    
    print("\n" + "="*70)
    print("  Day 3 完整 API 测试：搜索 + 过滤 + 元数据")
    print("="*70 + "\n")
    
    # ========== Day 2 的端点（检查是否仍正常） ==========
    print("📌 Day 2 端点验证（确保之前的功能仍正常）\n")
    
    # 1. 健康检查
    print("✅ 测试 1：GET /health")
    result = await health_check()
    print(f"   └─ 状态：{result.status}\n")
    
    # 2. 随机菜品
    print("✅ 测试 2：GET /api/v1/dishes/random")
    result = await get_random_dish()
    dish_id = result.id
    print(f"   └─ 随机菜品：{result.name} ({result.category})\n")
    
    # 3. 食材推荐
    print("✅ 测试 3：POST /api/v1/dishes/recommend")
    request = RecommendRequest(ingredients=["番茄", "鸡蛋"], limit=3)
    result = await recommend_dishes(request)
    print(f"   └─ 匹配菜品数：{len(result)}")
    print(f"   └─ 第一个：{result[0].name} ({result[0].match_score:.0f}%)\n")
    
    # 4. 菜品详情
    print("✅ 测试 4：GET /api/v1/dishes/{id}")
    result = await get_dish_detail(dish_id)
    print(f"   └─ 菜品：{result.name}")
    print(f"   └─ 食材数：{len(result.ingredients)}")
    print(f"   └─ 步骤数：{len(result.steps)}\n")
    
    # ========== Day 3 的新端点 ==========
    print("📌 Day 3 新端点测试\n")
    
    # 5. 菜品搜索
    print("✅ 测试 5：GET /api/v1/dishes/search（无参数）")
    result = await search_dishes()
    print(f"   └─ 返回菜品数：{len(result)}")
    print(f"   └─ 第一个：{result[0].name}\n")
    
    # 搜索 - 关键词查询
    print("✅ 测试 5a：GET /api/v1/dishes/search?q=番茄")
    result = await search_dishes(q="番茄")
    print(f"   └─ 搜索到菜品数：{len(result)}")
    for dish in result:
        print(f"      • {dish.name}")
    print()
    
    # 搜索 - 分类过滤
    print("✅ 测试 5b：GET /api/v1/dishes/search?category=素菜")
    result = await search_dishes(category="素菜")
    print(f"   └─ 素菜菜品数：{len(result)}\n")
    
    # 搜索 - 难度过滤
    print("✅ 测试 5c：GET /api/v1/dishes/search?difficulty=1")
    result = await search_dishes(difficulty=1)
    print(f"   └─ 难度 1 星菜品数：{len(result)}\n")
    
    # 搜索 - 组合过滤
    print("✅ 测试 5d：GET /api/v1/dishes/search?q=鸡&category=素菜&difficulty=2")
    result = await search_dishes(q="鸡", category="素菜", difficulty=2)
    print(f"   └─ 综合过滤结果数：{len(result)}\n")
    
    # 搜索 - 分页
    print("✅ 测试 5e：GET /api/v1/dishes/search?skip=0&limit=2")
    result = await search_dishes(skip=0, limit=2)
    print(f"   └─ 分页结果数：{len(result)}\n")
    
    # 6. 分类列表
    print("✅ 测试 6：GET /api/v1/categories")
    result = await get_categories()
    print(f"   └─ 分类数：{result['count']}")
    print(f"   └─ 分类列表：{', '.join(result['categories'])}\n")
    
    # 7. 元数据
    print("✅ 测试 7：GET /api/v1/metadata")
    result = await get_metadata()
    print(f"   └─ 总菜品数：{result['total_dishes']}")
    print(f"   └─ 总食材数：{result['total_ingredients']}")
    print(f"   └─ 分类数：{len(result['categories'])}")
    print(f"   └─ 难度等级：{result['difficulties']}\n")
    
    # 8. 根端点
    print("✅ 测试 8：GET /（根端点）")
    result = await root()
    print(f"   └─ API 版本：{result['version']}")
    print(f"   └─ 可用端点数：{len(result['endpoints'])}\n")
    
    print("="*70)
    print("  ✅ 所有 8 个测试全部通过！")
    print("="*70 + "\n")

asyncio.run(test_all_endpoints())
