# 🚀 后端 API 完整演示与说明

## 问题回答

### 1️⃣ 现在是否还在用示例菜数据？

**答：是的，目前使用示例数据，但已完全就绪可扩展。**

#### 当前数据库状态
```
📊 数据库：SQLite (/mnt/c/SearchMenu/backend/search_menu.db)

当前菜品数据：
1. 番茄炒鸡蛋 (素菜) - 难度：1星 ⭐
2. 西兰花炒鸡蛋 (素菜) - 难度：2星
3. 番茄鸡汤 (汤与粥) - 难度：2星
4. 清炒青菜 (素菜) - 难度：1星 ⭐
5. 红豆薏米粥 (汤与粥) - 难度：2星

统计信息：
- 总菜品数：5 道
- 总食材数：14 种
- 分类数：2 个（素菜、汤与粥）
```

#### 如何扩展数据

**方式 1：直接数据库插入**
```python
from app.database import SessionLocal
from app.models import Dish

db = SessionLocal()
new_dish = Dish(
    name="红烧肉",
    category="肉类",
    difficulty=3,
    description="经典红烧肉，肥而不腻",
    estimated_time="90分钟"
)
db.add(new_dish)
db.commit()
db.close()
```

**方式 2：修改 init_db.py 增加更多示例菜品**

编辑 `backend/scripts/init_db.py`，在 `sample_dishes` 列表中追加更多菜品，然后运行：
```bash
cd /mnt/c/SearchMenu/backend
python3 scripts/init_db.py
```

**方式 3：从 HowToCook 项目导入真实菜品**

计划在后续版本集成 HowToCook 数据源。

---

### 2️⃣ 各个端点的具体功能举例

#### 📍 API 端点完整演示

##### 1️⃣ **健康检查** (GET /health)
```bash
$ curl http://localhost:8000/health
```
**响应：**
```json
{
    "status": "ok",
    "message": "SearchMenu API 服务正常运行 🎉",
    "timestamp": "2026-02-15T07:39:40.785871"
}
```
**用途：** 检查 API 服务是否在线

---

##### 2️⃣ **获取随机菜品** (GET /api/v1/dishes/random)
```bash
$ curl http://localhost:8000/api/v1/dishes/random
```
**响应示例：**
```json
{
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    "difficulty": 1,
    "description": "简单易做的经典家常菜，富含蛋白质和维生素",
    "estimated_time": "15分钟",
    "id": "295ef540-78d2-4989-abd6-538c1e9b555f",
    "ingredients": [
        {
            "ingredient_name": "番茄",
            "quantity": "2个",
            "is_main": true
        },
        {
            "ingredient_name": "鸡蛋",
            "quantity": "3个",
            "is_main": true
        }
    ],
    "steps": [
        {
            "step_number": 1,
            "description": "番茄切块，鸡蛋打散",
            "duration": "2分钟"
        }
    ]
}
```
**用途：** 随机推荐一道菜品（前端"今日推荐"功能）

---

##### 3️⃣ **菜品搜索** (GET /api/v1/dishes/search)

###### 3a. 无参数 - 获取所有菜品
```bash
$ curl http://localhost:8000/api/v1/dishes/search
```
**结果：** 返回所有 5 道菜品（简略信息）

###### 3b. 关键词搜索
```bash
$ curl "http://localhost:8000/api/v1/dishes/search?q=%E7%95%AA%E8%8C%84"
# 实际查询：q=番茄
```
**结果：** 返回 2 道含有"番茄"的菜品
- 番茄炒鸡蛋
- 番茄鸡汤

###### 3c. 分类过滤
```bash
$ curl "http://localhost:8000/api/v1/dishes/search?category=%E7%B4%A0%E8%8F%9C"
# 实际查询：category=素菜
```
**结果：** 返回 3 道素菜
- 番茄炒鸡蛋
- 西兰花炒鸡蛋
- 清炒青菜

###### 3d. 难度过滤
```bash
$ curl "http://localhost:8000/api/v1/dishes/search?difficulty=1"
```
**结果：** 返回 2 道 1 星简单菜品
- 番茄炒鸡蛋
- 清炒青菜

###### 3e. 多条件组合
```bash
$ curl "http://localhost:8000/api/v1/dishes/search?category=%E7%B4%A0%E8%8F%9C&difficulty=1"
# 实际查询：category=素菜&difficulty=1
```
**结果：** 返回 2 道"简单素菜"

###### 3f. 分页获取
```bash
$ curl "http://localhost:8000/api/v1/dishes/search?skip=0&limit=2"
```
**结果：** 返回第 1-2 道菜品

---

##### 4️⃣ **获取分类列表** (GET /api/v1/categories)
```bash
$ curl http://localhost:8000/api/v1/categories
```
**响应：**
```json
{
    "categories": ["汤与粥", "素菜"],
    "count": 2
}
```
**用途：** 前端用于构建"分类过滤"下拉菜单

---

##### 5️⃣ **获取系统元数据** (GET /api/v1/metadata)
```bash
$ curl http://localhost:8000/api/v1/metadata
```
**响应：**
```json
{
    "total_dishes": 5,
    "categories": ["汤与粥", "素菜"],
    "difficulties": [1, 2, 3, 4, 5],
    "total_ingredients": 14,
    "api_version": "1.0.0"
}
```
**用途：** 前端初始化时获取系统配置和统计信息

---

##### 6️⃣ **菜品详情** (GET /api/v1/dishes/{dish_id})
```bash
$ curl "http://localhost:8000/api/v1/dishes/295ef540-78d2-4989-abd6-538c1e9b555f"
```
**响应：** 完整菜品信息（包括所有食材和烹饪步骤）
```json
{
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    "difficulty": 1,
    "ingredients": [
        {
            "ingredient_name": "番茄",
            "quantity": "2个",
            "is_main": true
        },
        {
            "ingredient_name": "鸡蛋",
            "quantity": "3个",
            "is_main": true
        },
        {
            "ingredient_name": "食用油",
            "quantity": "15ml",
            "is_main": false
        },
        {
            "ingredient_name": "盐",
            "quantity": "适量",
            "is_main": false
        }
    ],
    "steps": [
        {
            "step_number": 1,
            "description": "番茄切块，鸡蛋打散",
            "duration": "2分钟"
        },
        {
            "step_number": 2,
            "description": "热锅下油，炒鸡蛋至半熟",
            "duration": "3分钟"
        },
        {
            "step_number": 3,
            "description": "加入番茄块翻炒",
            "duration": "3分钟"
        },
        {
            "step_number": 4,
            "description": "加盐调味，炒至番茄软化",
            "duration": "3分钟"
        }
    ]
}
```
**用途：** 前端点击菜品时显示完整详情和烹饪步骤

---

##### 7️⃣ **食材推荐** (POST /api/v1/dishes/recommend)
```bash
$ curl -X POST http://localhost:8000/api/v1/dishes/recommend \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["鸡蛋", "番茄"]}'
```
**响应：** 根据食材匹配的菜品列表（按匹配度排序）
```json
[
    {
        "dish_id": "295ef540-78d2-4989-abd6-538c1e9b555f",
        "name": "番茄炒鸡蛋",
        "category": "素菜",
        "difficulty": 1,
        "match_score": 50.0,
        "matched_ingredients": ["番茄", "鸡蛋"]
    },
    {
        "dish_id": "897bbce9-942a-4252-82fb-2388c720b2c8",
        "name": "西兰花炒鸡蛋",
        "category": "素菜",
        "difficulty": 2,
        "match_score": 25.0,
        "matched_ingredients": ["鸡蛋"]
    },
    {
        "dish_id": "384d12e6-09ce-449f-b37f-e45e46010d6f",
        "name": "番茄鸡汤",
        "category": "汤与粥",
        "difficulty": 2,
        "match_score": 20.0,
        "matched_ingredients": ["番茄"]
    }
]
```
**用途：** 用户输入有的食材后，推荐相关菜品

---

## 3️⃣ 后端运行演示 Demo

### 环境前置条件
```bash
# 进入后端目录
cd /mnt/c/SearchMenu/backend

# 确保虚拟环境激活
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 确保依赖已安装
pip install -r requirements.txt
```

### 启动后端服务
```bash
# 方式 1：使用 uvicorn 启动
python -m uvicorn app.main:app --reload --port 8000

# 方式 2：后台启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 输出应该显示：
# INFO:     Uvicorn running on http://0.0.0.0:8000
# ✅ SearchMenu API 已启动
# 📖 API 文档：http://localhost:8000/docs
# 🔗 备用文档：http://localhost:8000/redoc
```

### 访问 Swagger 自动文档
打开浏览器访问：
```
http://localhost:8000/docs
```

你将看到：
- 所有 7 个 API 端点的完整说明
- 参数描述和类型验证
- 在线测试工具（Try it out）
- 请求/响应示例

### 快速测试脚本

我已为你创建了完整的演示脚本：

```bash
# 运行演示脚本（展示所有 API 端点）
bash /tmp/api_demo_fixed.sh
```

**输出示例：**
```
🚀 ========== SearchMenu API 完整演示（已修复） ==========

📍 1️⃣ 健康检查 (GET /health)
─────────────────────────────
{
    "status": "ok",
    "message": "SearchMenu API 服务正常运行 🎉",
    ...
}

📍 2️⃣ 随机菜品 (GET /api/v1/dishes/random)
─────────────────────────────
{
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    ...
}

... (更多示例)

✅ API 演示完成！
```

---

## 🎯 前端开发时需要知道的

### 各端点的前端使用场景

| 端点 | 前端场景 | 参数说明 |
|------|---------|--------|
| `GET /health` | 应用启动时检查服务可用性 | 无 |
| `GET /api/v1/dishes/random` | "今日推荐"功能 | 可选：category, difficulty |
| `GET /api/v1/dishes/search` | 菜品列表展示、搜索、过滤 | q, category, difficulty, skip, limit |
| `GET /api/v1/categories` | 分类下拉菜单 | 无 |
| `GET /api/v1/metadata` | 系统初始化（获取统计信息） | 无 |
| `GET /api/v1/dishes/{id}` | 菜品详情页面 | dish_id |
| `POST /api/v1/dishes/recommend` | 基于食材的菜品推荐 | ingredients (数组) |

### 数据结构参考

**DishSimple**（简略菜品）
```json
{
    "id": "string (UUID)",
    "name": "string",
    "category": "string",
    "difficulty": 1-5,
    "description": "string",
    "estimated_time": "string",
    "image_url": "string or null",
    "github_url": "string or null",
    "created_at": "datetime"
}
```

**DishDetail**（完整菜品）
```json
{
    "id": "string (UUID)",
    "name": "string",
    "category": "string",
    "difficulty": 1-5,
    "description": "string",
    "estimated_time": "string",
    "ingredients": [
        {
            "ingredient_name": "string",
            "quantity": "string",
            "is_main": boolean,
            "is_optional": boolean
        }
    ],
    "steps": [
        {
            "step_number": int,
            "description": "string",
            "duration": "string"
        }
    ],
    "image_url": "string or null",
    "github_url": "string or null",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

---

## ✅ 总结

| 问题 | 答案 |
|------|------|
| 是否用示例数据？ | ✅ 是，已初始化 5 道菜品，完全就绪可扩展 |
| 端点功能举例说明？ | ✅ 提供了 7 个端点的详细说明和 curl 命令 |
| 有无运行 demo？ | ✅ 已启动服务，提供演示脚本和 Swagger 文档 |

**后端状态：✅ 已完全可用，可开始前端开发**

访问 http://localhost:8000/docs 查看交互式 API 文档！
