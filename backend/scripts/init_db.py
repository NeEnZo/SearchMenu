import sys
import os
import re
from pathlib import Path

# 添加父目录到 Python 路径，以便导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 确保数据库路径正确
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, SessionLocal
from app.models import Dish, Ingredient, DishIngredient, CookingStep
import uuid

# ============================================================================
# HowToCook 数据解析函数
# ============================================================================

def parse_difficulty_from_stars(text: str) -> int:
    """从星号提取难度等级（★ 表示1，★★ 表示2，等等）"""
    if not text:
        return 3  # 默认中等难度
    matches = re.findall(r'★+', text)
    if matches:
        return min(len(matches[0]), 5)  # 最多5星
    return 3

def extract_ingredients(content: str) -> list:
    """从markdown内容中提取食材列表（支持 * 和 - 两种列表格式）"""
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
    
    # 提取 * 或 - 开头的行作为食材（HowToCook 两种格式都有）
    lines = section.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* ') or stripped.startswith('- '):
            ingredient = stripped[2:].strip()
            if ingredient:
                ingredients.append(ingredient)
    
    return ingredients[:20]  # 限制在20个食材以内

def extract_cooking_steps(content: str) -> list:
    """从markdown内容中提取烹饪步骤（支持 * 和 - 两种列表格式）"""
    steps = []
    
    # 查找 "操作" 部分
    if "## 操作" not in content:
        return steps
    
    start_idx = content.find("## 操作")
    end_markers = ["## 附加内容", "如果您遵循"]
    end_idx = len(content)
    
    # 找下一个 ## 标题（但不能是 ## 操作 本身）
    next_section = re.search(r'\n## ', content[start_idx + 3:])
    if next_section:
        end_idx = min(end_idx, start_idx + 3 + next_section.start())
    
    for marker in end_markers:
        idx = content.find(marker, start_idx)
        if idx > start_idx:
            end_idx = min(end_idx, idx)
    
    section = content[start_idx:end_idx]
    
    # 提取 * 或 - 开头的行作为步骤（HowToCook 两种格式都有）
    lines = section.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('* ') or stripped.startswith('- '):
            step = stripped[2:].strip()
            if step:
                steps.append(step)
    
    return steps[:15]  # 限制在15个步骤以内

def parse_dish_file(filepath: str) -> dict:
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
    
    # 如果没有食材或步骤，跳过该菜品（数据不完整）
    # 不再用菜名关键词提取食材，避免产生"鸡""蛋""肉"等错误数据
    if not ingredients:
        ingredients = ['（食材信息待完善）']
    
    if not steps:
        steps = ['（步骤信息待完善，请参阅 HowToCook 原始文档）']
    
    return {
        'name': dish_name,
        'category': 'HowToCook',  # 稍后会根据目录改变
        'difficulty': difficulty,
        'description': f"来自HowToCook：{dish_name}",
        'estimated_time': "30分钟",
        'ingredients': ingredients,
        'steps': steps,
    }

def scan_howtocook_dishes(base_path: str) -> list:
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


# ============================================================================
# 初始化数据库
# ============================================================================

# 初始化数据库表
print("🔧 正在初始化数据库表...")
init_db()
print("✅ 数据库表创建成功\n")

# 获取数据库会话
db = SessionLocal()

# 自动推导 how-to-cook-data 目录（兼容本地开发和 Docker 构建）
_script_dir = Path(__file__).parent
_candidates = [
    os.environ.get('HOWTOCOOK_DATA_PATH', ''),
    str(_script_dir.parent / 'how-to-cook-data'),        # Docker: /build/how-to-cook-data
    str(_script_dir.parent.parent / 'how-to-cook-data'), # 本地: SearchMenu/how-to-cook-data
]
howtocook_path = next((p for p in _candidates if p and os.path.isdir(p)), None)
if not howtocook_path:
    print("❌ 找不到 how-to-cook-data 目录，请设置 HOWTOCOOK_DATA_PATH 环境变量")
    db.close()
    exit(1)

print(f"📂 正在扫描 HowToCook 数据目录: {howtocook_path}\n")

sample_dishes = scan_howtocook_dishes(howtocook_path)

if not sample_dishes:
    print("❌ 未找到任何菜品数据！")
    db.close()
    exit(1)

print(f"\n📝 正在导入 {len(sample_dishes)} 个菜品...\n")

# 导入菜品数据
imported_count = 0
for dish_data in sample_dishes:
    try:
        # 创建菜品
        dish = Dish(
            id=str(uuid.uuid4()),
            name=dish_data["name"],
            category=dish_data["category"],
            difficulty=dish_data["difficulty"],
            description=dish_data["description"],
            estimated_time=dish_data["estimated_time"],
            github_url="https://github.com/Anduin2017/HowToCook"
        )
        db.add(dish)
        db.flush()
        
        # 添加食材
        for idx, ingredient_name in enumerate(dish_data["ingredients"], 1):
            # 查询或创建食材
            ingredient = db.query(Ingredient).filter(
                Ingredient.name == ingredient_name
            ).first()
            
            if not ingredient:
                ingredient = Ingredient(
                    id=str(uuid.uuid4()),
                    name=ingredient_name,
                    normalized_name=ingredient_name.lower()
                )
                db.add(ingredient)
                db.flush()
            
            # 创建菜品-食材关联
            dish_ing = DishIngredient(
                id=str(uuid.uuid4()),
                dish_id=dish.id,
                ingredient_id=ingredient.id,
                quantity="適量",  # HowToCook 已包含在食材名中
                is_main=(idx <= 3)  # 假设前3个是主食材
            )
            db.add(dish_ing)
        
        # 添加步骤
        for step_number, step_desc in enumerate(dish_data["steps"], 1):
            step = CookingStep(
                id=str(uuid.uuid4()),
                dish_id=dish.id,
                step_number=step_number,
                description=step_desc,
                duration="3分钟"  # 默认时间
            )
            db.add(step)
        
        db.flush()
        imported_count += 1
        if imported_count % 10 == 0:
            print(f"  ✅ 已导入 {imported_count} 道菜品...")
    
    except Exception as e:
        print(f"  ⚠️  导入菜品 '{dish_data['name']}' 失败: {e}")
        continue

# 提交事务
db.commit()
db.close()

print(f"\n✅ 数据导入完成！\n")
print("📊 数据统计：")
print(f"   • 导入菜品数量：{imported_count}/{len(sample_dishes)}")
print(f"   • 数据库文件：/mnt/c/SearchMenu/backend/search_menu.db")
print(f"   • 数据来源：HowToCook (https://github.com/Anduin2017/HowToCook)")
print(f"\n🎉 数据库初始化完成！")
