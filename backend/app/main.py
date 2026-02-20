"""
SearchMenu FastAPI 应用
用途：菜品随机推荐、食材匹配推荐、搜索、查详情
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.database import get_db, SessionLocal
from app.models import Dish, Ingredient, DishIngredient, CookingStep

# ============================================================================
# 1. 创建 FastAPI 应用实例
# ============================================================================
app = FastAPI(
    title="SearchMenu API",
    description="菜品推荐系统 API",
    version="1.0.0",
)

# ============================================================================
# 2. 配置 CORS（跨域资源共享）
# ============================================================================
# 生产环境通过 ALLOWED_ORIGINS 环境变量指定前端域名（逗号分隔），
# 未设置时允许所有源（本地开发模式）。
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
if _raw_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 3. Pydantic 数据模型（请求/响应格式）
# ============================================================================

class IngredientInfo(BaseModel):
    """食材信息"""
    name: str
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


class CookingStepInfo(BaseModel):
    """烹饪步骤"""
    step_number: int
    description: str
    duration: Optional[str] = None
    
    class Config:
        from_attributes = True


class DishIngredientInfo(BaseModel):
    """菜品食材详细信息"""
    ingredient_name: str
    quantity: str
    is_main: bool = False
    is_optional: bool = False


class DishBase(BaseModel):
    """菜品基础信息"""
    name: str
    category: str
    difficulty: int
    description: Optional[str] = None
    estimated_time: Optional[str] = None
    image_url: Optional[str] = None
    github_url: Optional[str] = None


class DishDetail(DishBase):
    """菜品详细信息（包含食材和步骤）"""
    id: str
    ingredients: List[DishIngredientInfo] = []
    steps: List[CookingStepInfo] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DishSimple(DishBase):
    """菜品简略信息（不含步骤）"""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecommendRequest(BaseModel):
    """推荐请求数据"""
    ingredients: List[str]                         # 用户输入的食材列表，如 ["番茄", "鸡蛋"]
    limit: int = 10                                # 返回最多几个推荐


class RecommendResponse(BaseModel):
    """推荐响应数据"""
    dish_id: str
    name: str
    category: str
    difficulty: int
    description: Optional[str]
    estimated_time: Optional[str]
    match_score: float                             # 匹配分数（0-100%）
    matched_ingredients: List[str]                 # 匹配到的食材


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str                                    # "ok" 或 "error"
    message: str
    timestamp: datetime


class SearchResponse(BaseModel):
    """搜索响应数据"""
    dishes: List[DishSimple]
    total: int


# ============================================================================
# 4. 工具函数
# ============================================================================

def normalize_name(name: str) -> str:
    """规范化名称：转小写、去空格"""
    return name.lower().strip()


def calculate_match_score(user_ingredients: List[str], dish_ingredients: List[tuple]) -> tuple:
    """
    计算菜品与用户食材的匹配分数
    
    规则：
    - 只考虑「主食材」is_main=True，忽略辅料和调味料
    - 用户输入任意一种食材只要在主食材中有匹配就算成功
    - 匹配分数 = (匹配的主食材数 / 总主食材数) * 100
    
    支持三种匹配方式：
    1. 精确匹配：用户输入与食材名称完全相同（优先级最高）
    2. 包含匹配：用户输入是食材名称的一部分，且食材名长度 > 用户输入
    3. 同义词匹配：预定义的同义词列表
    
    返回: (匹配分数0-100, 匹配到的食材列表)
    """
    # 同义词映射（用户输入 -> 可能的食材关键字）
    synonyms = {
        '番茄': ['番茄', '西红柿', '番茄酱'],
        '西红柿': ['番茄', '西红柿', '番茄酱'],
        '土豆': ['土豆', '马铃薯'],
        '马铃薯': ['土豆', '马铃薯'],
        '鸡蛋': ['鸡蛋', '蛋'],
        '蛋': ['鸡蛋', '蛋'],
    }
    
    user_normalized = [normalize_name(ing) for ing in user_ingredients]
    matched_ingredients = []
    matched_count = 0
    total_main_ingredients = 0
    seen_ingredients = set()  # 防止同义词重复计数
    
    for ing_name, is_main, quantity in dish_ingredients:
        # 只计算主食材
        if not is_main:
            continue
        
        total_main_ingredients += 1
        ing_normalized = normalize_name(ing_name)
        is_matched = False
        matched_user_ing = None
        
        for user_ing in user_normalized:
            # 方式1: 精确匹配（优先级最高）
            if ing_normalized == user_ing:
                is_matched = True
                matched_user_ing = user_ing
                break
            
            # 方式2: 包含匹配
            # 只有当食材名长度 > 用户输入长度时才匹配
            # 这样"番茄"匹配"西红柿"，但"鸡"不匹配"鸡蛋"
            if user_ing in ing_normalized and len(ing_normalized) > len(user_ing):
                is_matched = True
                matched_user_ing = user_ing
                break
            
            # 方式3: 同义词匹配
            if user_ing in synonyms:
                for synonym in synonyms[user_ing]:
                    if normalize_name(synonym) == ing_normalized:
                        is_matched = True
                        matched_user_ing = user_ing
                        break
            
            if is_matched:
                break
        
        # 只有当这个用户输入食材还没被计数过时，才计数
        if is_matched and matched_user_ing and matched_user_ing not in seen_ingredients:
            matched_ingredients.append(ing_name)
            matched_count += 1
            seen_ingredients.add(matched_user_ing)
    
    # 计算匹配分数：(匹配主食材数 / 总主食材数) * 100
    if total_main_ingredients > 0:
        score = (matched_count / total_main_ingredients) * 100
    else:
        score = 0
    
    return min(score, 100), matched_ingredients


def format_dish_detail(dish_obj) -> DishDetail:
    """将数据库 Dish 对象转换为 DishDetail 响应"""
    ingredients = []
    for dish_ing in dish_obj.ingredients:
        ingredients.append(
            DishIngredientInfo(
                ingredient_name=dish_ing.ingredient.name,
                quantity=dish_ing.quantity,
                is_main=dish_ing.is_main,
                is_optional=dish_ing.is_optional,
            )
        )
    
    steps = []
    for step in dish_obj.steps:
        steps.append(
            CookingStepInfo(
                step_number=step.step_number,
                description=step.description,
                duration=step.duration,
            )
        )
    
    return DishDetail(
        id=dish_obj.id,
        name=dish_obj.name,
        category=dish_obj.category,
        difficulty=dish_obj.difficulty,
        description=dish_obj.description,
        estimated_time=dish_obj.estimated_time,
        image_url=dish_obj.image_url,
        github_url=dish_obj.github_url,
        ingredients=ingredients,
        steps=steps,
        created_at=dish_obj.created_at,
        updated_at=dish_obj.updated_at,
    )


# ============================================================================
# 5. API 端点
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    服务器健康检查端点
    
    用途：验证服务器是否正常运行
    响应：
    - status: "ok" 表示服务器正常
    - message: 详细信息
    - timestamp: 当前时间
    """
    return HealthResponse(
        status="ok",
        message="SearchMenu API 服务正常运行 🎉",
        timestamp=datetime.utcnow(),
    )


@app.get("/api/v1/dishes/random", response_model=DishDetail, tags=["Dishes"])
async def get_random_dish(category: Optional[str] = None, difficulty: Optional[int] = None):
    """
    获取随机菜品推荐
    
    参数：
    - category: 可选，菜品分类（如 "素菜", "汤与粥"）
    - difficulty: 可选，难度等级 1-5
    
    响应：完整菜品信息（含食材和步骤）
    
    示例：
    GET /api/v1/dishes/random
    GET /api/v1/dishes/random?category=素菜
    GET /api/v1/dishes/random?difficulty=1
    """
    import random
    
    db = SessionLocal()
    try:
        # 构建查询条件
        query = db.query(Dish)
        
        if category:
            query = query.filter(Dish.category == category)
        
        if difficulty:
            query = query.filter(Dish.difficulty == difficulty)
        
        # 获取所有符合条件的菜品
        dishes = query.all()
        
        if not dishes:
            return {
                "error": "未找到符合条件的菜品",
                "status": "no_data"
            }
        
        # 随机选择一道
        dish = random.choice(dishes)
        
        return format_dish_detail(dish)
    
    finally:
        db.close()


@app.post("/api/v1/dishes/recommend", response_model=List[RecommendResponse], tags=["Dishes"])
async def recommend_dishes(request: RecommendRequest, category: Optional[str] = None):
    """
    基于食材推荐菜品
    
    参数：
    {
        "ingredients": ["番茄", "鸡蛋"],
        "limit": 3
    }
    可选查询参数：
    - category: 限制菜品分类（如 "素菜"）
    
    响应：按匹配分数排序的菜品列表（只返回有匹配的菜品）
    
    匹配算法：
    - 仅考虑「主食材」(is_main=True)
    - 只要主食材中有任何用户输入的食材就算匹配
    - 匹配分数 = (匹配主食材数 / 总主食材数) * 100
    """
    db = SessionLocal()
    try:
        # 获取所有菜品，可选按分类过滤
        query = db.query(Dish)
        if category:
            query = query.filter(Dish.category == category)
        
        all_dishes = query.all()
        
        recommendations = []
        
        for dish in all_dishes:
            # 获取菜品的主食材（只取 is_main=True）
            dish_ingredients = [
                (ing.ingredient.name, ing.is_main, ing.quantity)
                for ing in dish.ingredients
                if ing.is_main  # 只考虑主食材
            ]
            
            # 如果没有主食材，跳过该菜品
            if not dish_ingredients:
                continue
            
            # 计算匹配分数
            score, matched_ings = calculate_match_score(request.ingredients, dish_ingredients)
            
            # 只保留有匹配的菜品（至少匹配一个主食材）
            if len(matched_ings) > 0:
                recommendations.append(
                    RecommendResponse(
                        dish_id=dish.id,
                        name=dish.name,
                        category=dish.category,
                        difficulty=dish.difficulty,
                        description=dish.description,
                        estimated_time=dish.estimated_time,
                        match_score=score,
                        matched_ingredients=matched_ings,
                    )
                )
        
        # 按匹配分数降序排序，相同分数随机顺序
        import random
        
        # 排序规则：
        # 1. 优先按匹配食材数量降序（多个食材匹配的菜品优先）
        # 2. 其次按匹配分数降序
        # 3. 同分数随机顺序
        recommendations.sort(key=lambda x: (
            -len(x.matched_ingredients),  # 匹配食材数多的优先
            -x.match_score,                # 匹配分数高的优先
            random.random()                # 同分数随机
        ))
        
        # 限制返回数量
        return recommendations[:request.limit]
    
    finally:
        db.close()


# ============================================================================
# 4. 搜索菜品（必须放在 {dish_id} 之前，否则会被当成 ID）
# ============================================================================

@app.get("/api/v1/dishes/search", response_model=SearchResponse, tags=["Dishes"])
async def search_dishes(
    q: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    skip: int = 0,
    limit: int = 10
):
    """
    搜索菜品（支持多个过滤条件，包括食材搜索）
    
    参数：
    - q: 搜索关键词（菜品名称、描述或食材，至少2个字符）
    - category: 菜品分类（可选）
    - difficulty: 难度等级 1-5（可选）
    - skip: 跳过前 N 条（分页用）
    - limit: 返回最多 N 条
    
    示例：
    GET /api/v1/dishes/search?q=番茄
    GET /api/v1/dishes/search?q=鸡蛋
    GET /api/v1/dishes/search?category=素菜&difficulty=1
    """
    db = SessionLocal()
    try:
        # 开始查询所有符合分类和难度的菜品
        query = db.query(Dish).distinct()
        
        if category and category.strip():
            query = query.filter(Dish.category == category)
        
        if difficulty:
            difficulty = int(difficulty)
            if 1 <= difficulty <= 5:
                query = query.filter(Dish.difficulty == difficulty)
        
        # 按关键词搜索
        if q and q.strip():
            q = q.strip()
            # 避免单字搜索导致的模糊匹配（除非是菜品名中的关键词）
            if len(q) < 2:
                # 单字搜索仅搜索菜品名称，不搜索食材
                all_matching_dishes = query.all()
                filtered_dishes = []
                for dish in all_matching_dishes:
                    if q.lower() in dish.name.lower() or (dish.description and q.lower() in dish.description.lower()):
                        filtered_dishes.append(dish)
            else:
                # 多字搜索：搜索菜品名、描述和食材
                q_lower = q.lower()
                all_matching_dishes = query.all()
                filtered_dishes = []
                
                for dish in all_matching_dishes:
                    # 菜品名或描述包含关键词
                    if q_lower in dish.name.lower() or (dish.description and q_lower in dish.description.lower()):
                        filtered_dishes.append(dish)
                        continue
                    
                    # 食材搜索：检查菜品的食材名称
                    for dish_ing in dish.ingredients:
                        ing_name = dish_ing.ingredient.name
                        # 精确匹配食材或完整包含（避免"鸡"匹配"鸡蛋"）
                        if q_lower == ing_name.lower() or q in ing_name:
                            filtered_dishes.append(dish)
                            break
            
            # 获取总数和分页结果
            total_count = len(filtered_dishes)
            paginated_dishes = filtered_dishes[skip:skip + limit]
            
            return SearchResponse(
                dishes=paginated_dishes,
                total=total_count
            )
        
        # 如果没有搜索词，直接分页返回
        total_count = query.count()
        dishes = query.offset(skip).limit(limit).all()
        
        return SearchResponse(
            dishes=dishes,
            total=total_count
        )
    
    finally:
        db.close()


# ============================================================================
# 5. 菜品详情（放在 search 之后）
# ============================================================================

@app.get("/api/v1/dishes/{dish_id}", response_model=DishDetail, tags=["Dishes"])
async def get_dish_detail(dish_id: str):
    """
    获取菜品详细信息
    
    参数：
    - dish_id: 菜品 ID
    
    响应：包含食材列表和烹饪步骤的完整菜品信息
    """
    db = SessionLocal()
    try:
        dish = db.query(Dish).filter(Dish.id == dish_id).first()
        
        if not dish:
            # 无法返回dict，改为返回None后由FastAPI处理
            return None
        
        return format_dish_detail(dish)
    
    finally:
        db.close()


# ============================================================================
# 6. 应用启动和关闭事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("✅ SearchMenu API 已启动")
    print("📖 API 文档：http://localhost:8000/docs")
    print("🔗 备用文档：http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("🛑 SearchMenu API 已关闭")


@app.get("/api/v1/categories", tags=["Metadata"])
async def get_categories():
    """
    获取所有菜品分类列表
    
    响应：
    {
        "categories": ["素菜", "荤菜", "汤与粥", ...]
    }
    """
    db = SessionLocal()
    try:
        # 获取所有不重复的分类
        categories = db.query(Dish.category).distinct().all()
        
        # 转换为列表
        category_list = sorted([cat[0] for cat in categories if cat[0]])
        
        return {
            "categories": category_list,
            "count": len(category_list)
        }
    
    finally:
        db.close()


@app.get("/api/v1/metadata", tags=["Metadata"])
async def get_metadata():
    """
    获取菜品系统的元数据（统计信息）
    
    响应包含：
    - 总菜品数
    - 所有分类列表
    - 难度等级范围
    - 总食材数
    """
    db = SessionLocal()
    try:
        # 菜品数量
        total_dishes = db.query(Dish).count()
        
        # 分类列表
        categories = db.query(Dish.category).distinct().all()
        category_list = sorted([cat[0] for cat in categories if cat[0]])
        
        # 食材数量
        total_ingredients = db.query(Ingredient).count()
        
        return {
            "total_dishes": total_dishes,
            "categories": category_list,
            "difficulties": [1, 2, 3, 4, 5],
            "total_ingredients": total_ingredients,
            "api_version": "1.0.0",
        }
    
    finally:
        db.close()


@app.get("/", tags=["System"])
async def root():
    """根路由，返回 API 信息"""
    return {
        "name": "SearchMenu API",
        "version": "1.0.0",
        "description": "菜品推荐系统",
        "docs": "/docs",
        "endpoints": {
            "健康检查": "GET /health",
            "随机菜品": "GET /api/v1/dishes/random",
            "推荐菜品": "POST /api/v1/dishes/recommend",
            "菜品详情": "GET /api/v1/dishes/{dish_id}",
            "菜品搜索": "GET /api/v1/dishes/search",
            "分类列表": "GET /api/v1/categories",
            "系统元数据": "GET /api/v1/metadata",
        }
    }


# ============================================================================
# 8. 自定义异常处理（可选扩展）
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """捕获所有未处理的异常"""
    return {
        "status": "error",
        "message": str(exc),
        "timestamp": datetime.utcnow(),
    }
