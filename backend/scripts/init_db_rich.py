"""
增强版数据库初始化脚本 - 包含真实菜品数据
包含来自HowToCook等来源的丰富菜品数据
"""

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Dish, Ingredient, DishIngredient, CookingStep
from app.database import DATABASE_URL

# 初始化数据库连接
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# 丰富的菜品数据库
DISHES_DATA = [
    {
        "name": "番茄鸡蛋面",
        "category": "面食",
        "difficulty": 1,
        "description": "简单易学的家常面食，酸爽可口",
        "estimated_time": "15分钟",
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400",
        "ingredients": [
            {"name": "番茄", "quantity": "2个", "is_main": True},
            {"name": "鸡蛋", "quantity": "2个", "is_main": True},
            {"name": "面条", "quantity": "100g", "is_main": True},
            {"name": "生抽", "quantity": "2汤匙", "is_main": False},
            {"name": "植物油", "quantity": "2汤匙", "is_main": False},
            {"name": "盐", "quantity": "适量", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "将番茄切成块，鸡蛋打入碗中并搅匀", "duration": "5分钟"},
            {"step_number": 2, "description": "烧热锅中的油，炒制鸡蛋至半熟盛出", "duration": "3分钟"},
            {"step_number": 3, "description": "再加油，炒番茄块至出汁，加入鸡蛋混合", "duration": "5分钟"},
            {"step_number": 4, "description": "煮面条，加入番茄鸡蛋汤汁，调味即可", "duration": "7分钟"},
        ],
    },
    {
        "name": "清炒时蔬",
        "category": "素菜",
        "difficulty": 1,
        "description": "清淡健康的蔬菜炒菜，营养丰富",
        "estimated_time": "10分钟",
        "image_url": "https://images.unsplash.com/photo-1609501676725-7186f017a4b5?w=400",
        "ingredients": [
            {"name": "青菜", "quantity": "200g", "is_main": True},
            {"name": "胡萝卜", "quantity": "100g", "is_main": True},
            {"name": "蘑菇", "quantity": "100g", "is_main": True},
            {"name": "植物油", "quantity": "2汤匙", "is_main": False},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "大蒜", "quantity": "2瓣", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "将所有蔬菜洗净，切成合适大小的块状", "duration": "5分钟"},
            {"step_number": 2, "description": "热锅下油，炒香蒜末", "duration": "1分钟"},
            {"step_number": 3, "description": "依次加入胡萝卜、蘑菇、青菜翻炒", "duration": "5分钟"},
            {"step_number": 4, "description": "加盐调味，翻炒均匀即可出锅", "duration": "2分钟"},
        ],
    },
    {
        "name": "番茄汤",
        "category": "汤与粥",
        "difficulty": 1,
        "description": "酸酸的番茄汤，开胃又健康",
        "estimated_time": "20分钟",
        "image_url": "https://images.unsplash.com/photo-1571877227200-a0ca208ce7e8?w=400",
        "ingredients": [
            {"name": "番茄", "quantity": "3个", "is_main": True},
            {"name": "鸡蛋", "quantity": "1个", "is_main": False},
            {"name": "清汤", "quantity": "1升", "is_main": True},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "胡椒粉", "quantity": "少许", "is_main": False},
            {"name": "香油", "quantity": "1汤匙", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "番茄用热水烫后去皮，切成块状", "duration": "5分钟"},
            {"step_number": 2, "description": "烧热锅，炒番茄块至软烂出汁", "duration": "5分钟"},
            {"step_number": 3, "description": "加入清汤烧开，煮2分钟", "duration": "3分钟"},
            {"step_number": 4, "description": "打入鸡蛋，慢慢搅拌形成蛋花", "duration": "3分钟"},
            {"step_number": 5, "description": "加盐和胡椒粉调味，淋上香油即可", "duration": "2分钟"},
        ],
    },
    {
        "name": "蒜蓉炒菠菜",
        "category": "素菜",
        "difficulty": 1,
        "description": "经典素菜，蒜香十足",
        "estimated_time": "8分钟",
        "image_url": "https://images.unsplash.com/photo-1609501676725-7186f017a4b5?w=400",
        "ingredients": [
            {"name": "菠菜", "quantity": "300g", "is_main": True},
            {"name": "大蒜", "quantity": "4瓣", "is_main": False},
            {"name": "植物油", "quantity": "3汤匙", "is_main": False},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "生抽", "quantity": "1汤匙", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "菠菜洗净，大蒜切成蒜末", "duration": "3分钟"},
            {"step_number": 2, "description": "烧水至沸，下菠菜焯2分钟后沥干", "duration": "3分钟"},
            {"step_number": 3, "description": "热锅下油，炒香蒜末", "duration": "1分钟"},
            {"step_number": 4, "description": "加入菠菜翻炒，加生抽和盐调味", "duration": "2分钟"},
        ],
    },
    {
        "name": "糖醋排骨",
        "category": "荤菜",
        "difficulty": 2,
        "description": "酸甜适口，老少皆宜",
        "estimated_time": "45分钟",
        "image_url": "https://images.unsplash.com/photo-1634021165167-5f45cecc59d8?w=400",
        "ingredients": [
            {"name": "排骨", "quantity": "600g", "is_main": True},
            {"name": "白醋", "quantity": "4汤匙", "is_main": True},
            {"name": "白糖", "quantity": "4汤匙", "is_main": True},
            {"name": "生抽", "quantity": "3汤匙", "is_main": False},
            {"name": "姜", "quantity": "3片", "is_main": False},
            {"name": "植物油", "quantity": "3汤匙", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "排骨洗净，冷水下锅焯去血水，沥干", "duration": "10分钟"},
            {"step_number": 2, "description": "热锅下油，放入姜片爆香，再加排骨炒至变色", "duration": "5分钟"},
            {"step_number": 3, "description": "加生抽、白糖、白醋和适量水，烧开后转小火", "duration": "5分钟"},
            {"step_number": 4, "description": "盖盖炖30分钟至排骨软烂，汤汁收浓即可", "duration": "30分钟"},
        ],
    },
    {
        "name": "红烧肉",
        "category": "荤菜",
        "difficulty": 3,
        "description": "肥而不腻，入口即化",
        "estimated_time": "90分钟",
        "image_url": "https://images.unsplash.com/photo-1626082927389-6cd097cda688?w=400",
        "ingredients": [
            {"name": "五花肉", "quantity": "800g", "is_main": True},
            {"name": "冰糖", "quantity": "50g", "is_main": True},
            {"name": "生抽", "quantity": "5汤匙", "is_main": True},
            {"name": "老抽", "quantity": "3汤匙", "is_main": False},
            {"name": "姜", "quantity": "5片", "is_main": False},
            {"name": "葱", "quantity": "2根", "is_main": False},
            {"name": "八角", "quantity": "2个", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "五花肉切成2厘米见方的块，冷水下锅焯去血水", "duration": "10分钟"},
            {"step_number": 2, "description": "热锅下油，放入冰糖炒至焦糖色，加入肉块翻炒上色", "duration": "5分钟"},
            {"step_number": 3, "description": "加生抽、老抽、姜片、八角，倒入开水没过肉", "duration": "5分钟"},
            {"step_number": 4, "description": "烧开后转小火，加盖炖60分钟至肉软烂", "duration": "60分钟"},
            {"step_number": 5, "description": "加葱段，大火收汤至浓稠，出锅即可", "duration": "10分钟"},
        ],
    },
    {
        "name": "清汤面",
        "category": "面食",
        "difficulty": 1,
        "description": "清汤简单，清爽开胃",
        "estimated_time": "12分钟",
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400",
        "ingredients": [
            {"name": "面条", "quantity": "100g", "is_main": True},
            {"name": "清汤", "quantity": "500ml", "is_main": True},
            {"name": "青菜", "quantity": "50g", "is_main": False},
            {"name": "生抽", "quantity": "1汤匙", "is_main": False},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "葱", "quantity": "1根", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "清汤烧热，加生抽和盐调味", "duration": "3分钟"},
            {"step_number": 2, "description": "另起锅烧水煮面条至熟，沥干", "duration": "6分钟"},
            {"step_number": 3, "description": "将面条放入碗中，倒入热汤，加青菜和葱段", "duration": "2分钟"},
        ],
    },
    {
        "name": "宫保鸡丁",
        "category": "荤菜",
        "difficulty": 2,
        "description": "麻辣爽口，下饭绝配",
        "estimated_time": "20分钟",
        "image_url": "https://images.unsplash.com/photo-1609501676725-7186f017a4b5?w=400",
        "ingredients": [
            {"name": "鸡胸肉", "quantity": "300g", "is_main": True},
            {"name": "花生", "quantity": "100g", "is_main": True},
            {"name": "干辣椒", "quantity": "6个", "is_main": False},
            {"name": "生抽", "quantity": "2汤匙", "is_main": False},
            {"name": "白醋", "quantity": "1汤匙", "is_main": False},
            {"name": "白糖", "quantity": "1汤匙", "is_main": False},
            {"name": "花椒", "quantity": "1汤匙", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "鸡胸肉切成丁，用少量生抽腌制5分钟", "duration": "5分钟"},
            {"step_number": 2, "description": "热锅下油，炒鸡丁至变白盛出", "duration": "5分钟"},
            {"step_number": 3, "description": "锅中留油，炒干辣椒和花椒出香味", "duration": "2分钟"},
            {"step_number": 4, "description": "放入花生炒香，加鸡丁、生抽、白醋、白糖翻炒均匀", "duration": "5分钟"},
        ],
    },
    {
        "name": "鸡蛋炒青菜",
        "category": "素菜",
        "difficulty": 1,
        "description": "营养搭配合理，清淡可口",
        "estimated_time": "10分钟",
        "image_url": "https://images.unsplash.com/photo-1609501676725-7186f017a4b5?w=400",
        "ingredients": [
            {"name": "鸡蛋", "quantity": "2个", "is_main": True},
            {"name": "青菜", "quantity": "200g", "is_main": True},
            {"name": "植物油", "quantity": "2汤匙", "is_main": False},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "大蒜", "quantity": "2瓣", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "鸡蛋打入碗中搅匀，青菜洗净沥干，蒜切末", "duration": "3分钟"},
            {"step_number": 2, "description": "热锅下油，炒鸡蛋至半熟盛出", "duration": "2分钟"},
            {"step_number": 3, "description": "再加油炒蒜末，下青菜翻炒", "duration": "3分钟"},
            {"step_number": 4, "description": "加鸡蛋和盐，炒匀即可", "duration": "2分钟"},
        ],
    },
    {
        "name": "清粥配咸菜",
        "category": "汤与粥",
        "difficulty": 1,
        "description": "清汤白粥，清淡养胃",
        "estimated_time": "30分钟",
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400",
        "ingredients": [
            {"name": "米", "quantity": "100g", "is_main": True},
            {"name": "清水", "quantity": "1升", "is_main": True},
            {"name": "盐", "quantity": "适量", "is_main": False},
            {"name": "榨菜", "quantity": "50g", "is_main": False},
        ],
        "steps": [
            {"step_number": 1, "description": "米洗净，清水烧开放入米", "duration": "5分钟"},
            {"step_number": 2, "description": "烧开后转小火，盖盖煮25分钟至米开花", "duration": "25分钟"},
            {"step_number": 3, "description": "加盐调味，盛入碗中，配榨菜食用", "duration": "2分钟"},
        ],
    },
]

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    session = SessionLocal()
    
    try:
        # 收集所有食材
        ingredients_dict = {}
        
        for dish_data in DISHES_DATA:
            # 创建菜品
            dish_id = str(uuid.uuid4())
            dish = Dish(
                id=dish_id,
                name=dish_data["name"],
                category=dish_data["category"],
                difficulty=dish_data["difficulty"],
                description=dish_data["description"],
                estimated_time=dish_data["estimated_time"],
                image_url=dish_data["image_url"],
            )
            session.add(dish)
            
            # 添加食材和步骤
            for idx, ing_data in enumerate(dish_data["ingredients"], 1):
                ing_name = ing_data["name"]
                
                # 获取或创建食材
                if ing_name not in ingredients_dict:
                    ing_id = str(uuid.uuid4())
                    ingredient = Ingredient(
                        id=ing_id,
                        name=ing_name,
                        normalized_name=ing_name.lower(),
                    )
                    session.add(ingredient)
                    ingredients_dict[ing_name] = ingredient
                
                # 创建菜品-食材关联
                dish_ing = DishIngredient(
                    id=str(uuid.uuid4()),
                    dish_id=dish_id,
                    ingredient_id=ingredients_dict[ing_name].id,
                    quantity=ing_data["quantity"],
                    is_main=ing_data.get("is_main", False),
                )
                session.add(dish_ing)
            
            # 添加烹饪步骤
            for step_data in dish_data["steps"]:
                step = CookingStep(
                    id=str(uuid.uuid4()),
                    dish_id=dish_id,
                    step_number=step_data["step_number"],
                    description=step_data["description"],
                    duration=step_data.get("duration", ""),
                )
                session.add(step)
        
        session.commit()
        print(f"✅ 数据库初始化成功！")
        print(f"   创建了 {len(DISHES_DATA)} 道菜品")
        print(f"   创建了 {len(ingredients_dict)} 种食材")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
