from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Dish(Base):
    """菜品表"""
    __tablename__ = "dishes"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)  # 素菜、荤菜等
    difficulty = Column(Integer, default=3)  # 难度 1-5 星
    description = Column(Text)  # 菜品描述
    estimated_time = Column(String)  # 预计时间，如"15分钟"
    image_url = Column(String)  # 成品图片链接
    github_url = Column(String)  # GitHub 原菜谱链接
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ingredients = relationship("DishIngredient", back_populates="dish", cascade="all, delete-orphan")
    steps = relationship("CookingStep", back_populates="dish", cascade="all, delete-orphan")


class Ingredient(Base):
    """食材表"""
    __tablename__ = "ingredients"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)  # 标准食材名
    aliases = Column(String)  # 别名，逗号分隔（如"番茄,西红柿,华子"）
    category = Column(String)  # 食材分类：蔬菜、肉类、水产等
    normalized_name = Column(String, index=True)  # 规范化名称，用于模糊匹配
    
    # 关系
    dish_ingredients = relationship("DishIngredient", back_populates="ingredient")


class DishIngredient(Base):
    """菜品-食材关联表"""
    __tablename__ = "dish_ingredients"
    
    id = Column(String, primary_key=True)
    dish_id = Column(String, ForeignKey("dishes.id"), index=True)
    ingredient_id = Column(String, ForeignKey("ingredients.id"), index=True)
    quantity = Column(String)  # 数量，如"2个"、"100g"
    is_main = Column(Boolean, default=False)  # 是否为主料
    is_optional = Column(Boolean, default=False)  # 是否为可选
    
    # 关系
    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dish_ingredients")


class CookingStep(Base):
    """烹饪步骤表"""
    __tablename__ = "cooking_steps"
    
    id = Column(String, primary_key=True)
    dish_id = Column(String, ForeignKey("dishes.id"), index=True)
    step_number = Column(Integer)  # 步骤序号
    description = Column(Text)  # 步骤描述
    duration = Column(String)  # 预计耗时，如"10分钟"
    
    # 关系
    dish = relationship("Dish", back_populates="steps")
