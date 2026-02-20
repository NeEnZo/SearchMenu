"""
解析 HowToCook markdown 菜品数据
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def parse_difficulty_from_stars(text: str) -> int:
    """从星号提取难度等级（★ 表示1，★★ 表示2，等等）"""
    if not text:
        return 3  # 默认中等难度
    matches = re.findall(r'★+', text)
    if matches:
        return min(len(matches[0]), 5)  # 最多5星
    return 3

def extract_ingredients(content: str) -> List[str]:
    """从markdown内容中提取食材列表"""
    ingredients = []
    
    # 查找 "必备原料和工具" 部分
    if "必备原料和工具" not in content:
        return ingredients
    
    # 获取该部分的内容
    start_idx = content.find("必备原料和工具")
    end_markers = ["## 计算", "## 操作", "## 附加内容"]
    end_idx = len(content)
    
    for marker in end_markers:
        if marker in content[start_idx:]:
            idx = content.find(marker, start_idx)
            if idx > 0:
                end_idx = min(end_idx, idx)
    
    section = content[start_idx:end_idx]
    
    # 提取 * 开头的行作为食材
    lines = section.split('\n')
    for line in lines:
        if line.strip().startswith('*'):
            ingredient = line.strip()[1:].strip()
            if ingredient and not ingredient.startswith('*'):
                ingredients.append(ingredient)
    
    return ingredients[:20]  # 限制在20个食材以内

def extract_cooking_steps(content: str) -> List[str]:
    """从markdown内容中提取烹饪步骤"""
    steps = []
    
    # 查找 "操作" 部分
    if "## 操作" not in content:
        return steps
    
    start_idx = content.find("## 操作")
    end_markers = ["## 附加内容", "## ", "如果您遵循"]
    end_idx = len(content)
    
    for marker in end_markers:
        if marker in content[start_idx:]:
            idx = content.find(marker, start_idx)
            if idx > start_idx:
                end_idx = min(end_idx, idx)
    
    section = content[start_idx:end_idx]
    
    # 提取 * 开头的行作为步骤
    lines = section.split('\n')
    for line in lines:
        if line.strip().startswith('*'):
            step = line.strip()[1:].strip()
            if step and not step.startswith('*'):
                steps.append(step)
    
    return steps[:15]  # 限制在15个步骤以内

def parse_dish_file(filepath: str) -> Dict:
    """解析单个菜品markdown文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取菜品名（从第一行 # 标题）
    title_match = re.search(r'# (.+?)[\n$]', content)
    if not title_match:
        return None
    
    dish_name = title_match.group(1).strip().replace('的做法', '').replace('的方法', '')
    
    # 提取难度
    difficulty_match = re.search(r'预估烹饪难度：(.+?)[\n$]', content)
    difficulty = 3
    if difficulty_match:
        difficulty = parse_difficulty_from_stars(difficulty_match.group(1))
    
    # 提取食材
    ingredients = extract_ingredients(content)
    
    # 提取烹饪步骤
    steps = extract_cooking_steps(content)
    
    if not ingredients or not steps:
        return None  # 跳过数据不完整的菜品
    
    return {
        'name': dish_name,
        'category': 'HowToCook',  # 稍后会根据目录改变
        'difficulty': difficulty,
        'description': f"来自HowToCook：{dish_name}",
        'estimated_time': "30分钟",
        'ingredients': ingredients,
        'steps': steps,
    }

def scan_howtocook_dishes(base_path: str) -> List[Dict]:
    """扫描HowToCook目录，解析所有菜品"""
    dishes = []
    category_map = {
        'aquatic': '水产',
        'breakfast': '早餐',
        'condiment': '调味料',
        'dessert': '甜品',
        'drink': '饮品',
        'meat_dish': '肉类',
        'semi-finished': '半成品',
        'soup': '汤',
        'staple': '主食',
        'vegetable_dish': '蔬菜',
    }
    
    dishes_dir = os.path.join(base_path, 'dishes')
    if not os.path.exists(dishes_dir):
        print(f"❌ 找不到dishes目录: {dishes_dir}")
        return dishes
    
    # 遍历所有分类目录
    for category_en, category_zh in category_map.items():
        category_path = os.path.join(dishes_dir, category_en)
        if not os.path.isdir(category_path):
            continue
        
        # 递归查找所有.md文件
        for root, dirs, files in os.walk(category_path):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    dish = parse_dish_file(filepath)
                    if dish:
                        dish['category'] = category_zh
                        dishes.append(dish)
    
    return dishes

if __name__ == '__main__':
    howtocook_path = '/mnt/c/SearchMenu/how-to-cook-data'
    dishes = scan_howtocook_dishes(howtocook_path)
    print(f"✅ 找到 {len(dishes)} 道菜品")
    for dish in dishes[:5]:
        print(f"\n菜品: {dish['name']}")
        print(f"分类: {dish['category']}")
        print(f"难度: {'★' * dish['difficulty']}")
        print(f"食材数: {len(dish['ingredients'])}")
        print(f"步骤数: {len(dish['steps'])}")
