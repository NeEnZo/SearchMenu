#!/usr/bin/env python3
"""
API 测试脚本
运行方式：python test_api.py
"""

import requests
import json
import sys
import time
from datetime import datetime

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 颜色输出
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(title):
    """打印标题"""
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

def print_success(msg):
    """打印成功信息"""
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    """打印错误信息"""
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    """打印信息"""
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

def test_health():
    """测试健康检查端点"""
    print_header("测试 1：健康检查（/health）")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"服务器状态：{data.get('status')}")
            print_success(f"消息：{data.get('message')}")
            print_info(f"时间戳：{data.get('timestamp')}")
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"连接失败：{str(e)}")
        return False

def test_root():
    """测试根端点"""
    print_header("测试 2：根端点（/）")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API 名称：{data.get('name')}")
            print_success(f"版本：{data.get('version')}")
            print_info(f"描述：{data.get('description')}")
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"连接失败：{str(e)}")
        return False

def test_random_dish():
    """测试随机菜品推荐"""
    print_header("测试 3：随机菜品推荐（GET /api/v1/dishes/random）")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/dishes/random", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"菜品名：{data.get('name')}")
            print_success(f"分类：{data.get('category')}")
            print_success(f"难度：{'⭐' * data.get('difficulty', 0)}")
            print_success(f"预计时间：{data.get('estimated_time')}")
            print_info(f"食材数：{len(data.get('ingredients', []))}")
            print_info(f"步骤数：{len(data.get('steps', []))}")
            
            # 打印前两个食材
            ingredients = data.get('ingredients', [])
            if ingredients:
                print_info(f"食材示例：{ingredients[0]['ingredient_name']} ({ingredients[0]['quantity']})")
            
            # 打印第一个步骤
            steps = data.get('steps', [])
            if steps:
                print_info(f"步骤 1：{steps[0]['description']}")
            
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            print_info(f"响应：{response.text}")
            return False
    
    except Exception as e:
        print_error(f"连接失败：{str(e)}")
        return False

def test_recommend():
    """测试食材推荐"""
    print_header("测试 4：食材推荐（POST /api/v1/dishes/recommend）")
    
    try:
        payload = {
            "ingredients": ["番茄", "鸡蛋"],
            "limit": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/dishes/recommend",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"找到 {len(data)} 个匹配菜品")
            
            for i, dish in enumerate(data[:3], 1):  # 只显示前 3 个
                print(f"\n  {i}. {dish['name']}")
                print(f"     分类：{dish['category']}")
                print(f"     难度：{'⭐' * dish['difficulty']}")
                print(f"     匹配分数：{dish['match_score']:.1f}%")
                print(f"     匹配食材：{', '.join(dish['matched_ingredients'])}")
            
            return True
        else:
            print_error(f"HTTP {response.status_code}")
            print_info(f"响应：{response.text}")
            return False
    
    except Exception as e:
        print_error(f"连接失败：{str(e)}")
        return False

def main():
    """运行所有测试"""
    print(f"\n{BLUE}")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SearchMenu API 测试套件" + " " * 24 + "║")
    print("║" + " " * 15 + f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    print(f"{RESET}\n")
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("根端点", test_root()))
    results.append(("随机菜品", test_random_dish()))
    results.append(("食材推荐", test_recommend()))
    
    # 测试总结
    print_header("测试总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ 通过{RESET}" if result else f"{RED}❌ 失败{RESET}"
        print(f"  {name:20} {status}")
    
    print(f"\n{BLUE}总体进度：{passed}/{total} 测试通过{RESET}\n")
    
    if passed == total:
        print_success("所有测试通过！🎉")
        return 0
    else:
        print_error(f"{total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    # 给服务器 2 秒时间启动
    print_info("等待服务器启动...")
    time.sleep(2)
    
    sys.exit(main())
