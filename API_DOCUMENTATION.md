# 🎯 SearchMenu API 完整文档

## 📚 API 版本信息

- **API 版本**: 1.0.0
- **基础 URL**: `http://localhost:8000`
- **自动文档**: `http://localhost:8000/docs` (Swagger UI)
- **备用文档**: `http://localhost:8000/redoc` (ReDoc)

---

## 🚀 快速开始

### 启动服务器

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试所有端点

```bash
cd backend
python test_day3.py
```

---

## 📋 API 端点速查表

| 端点 | 方法 | 目的 | 参数 |
|------|------|------|------|
| `/health` | GET | 健康检查 | 无 |
| `/api/v1/dishes/random` | GET | 随机推荐 | category, difficulty |
| `/api/v1/dishes/recommend` | POST | 食材推荐 | ingredients, limit |
| `/api/v1/dishes/{dish_id}` | GET | 菜品详情 | dish_id |
| `/api/v1/dishes/search` | GET | **搜索菜品** | q, category, difficulty, skip, limit |
| `/api/v1/categories` | GET | **分类列表** | 无 |
| `/api/v1/metadata` | GET | **系统元数据** | 无 |

---

## 📖 详细 API 文档

### 1️⃣ 健康检查

**请求**
```bash
GET /health
```

**响应 (200 OK)**
```json
{
  "status": "ok",
  "message": "SearchMenu API 服务正常运行 🎉",
  "timestamp": "2026-02-15T14:30:00"
}
```

**用途**: 检查服务器是否正常运行

---

### 2️⃣ 随机菜品推荐

**请求**
```bash
# 获取任意随机菜品
GET /api/v1/dishes/random

# 获取某个分类的随机菜品
GET /api/v1/dishes/random?category=素菜

# 获取特定难度的随机菜品
GET /api/v1/dishes/random?difficulty=2

# 组合条件
GET /api/v1/dishes/random?category=素菜&difficulty=1
```

**响应 (200 OK)**
```json
{
  "id": "6766fcc0-83a6-42d1-ad11-7092be4fa3ae",
  "name": "番茄炒鸡蛋",
  "category": "素菜",
  "difficulty": 1,
  "description": "简单易做的经典家常菜，富含蛋白质和维生素",
  "estimated_time": "15分钟",
  "image_url": null,
  "github_url": "https://github.com/Anduin2017/HowToCook",
  "ingredients": [
    {
      "ingredient_name": "番茄",
      "quantity": "2个",
      "is_main": true,
      "is_optional": false
    },
    {
      "ingredient_name": "鸡蛋",
      "quantity": "3个",
      "is_main": true,
      "is_optional": false
    }
  ],
  "steps": [
    {
      "step_number": 1,
      "description": "番茄切块，鸡蛋打散",
      "duration": "2分钟"
    }
  ],
  "created_at": "2026-02-15T12:00:00",
  "updated_at": "2026-02-15T12:00:00"
}
```

---

### 3️⃣ 食材推荐

**请求**
```bash
POST /api/v1/dishes/recommend
Content-Type: application/json

{
  "ingredients": ["番茄", "鸡蛋"],
  "limit": 5
}
```

**响应 (200 OK)**
```json
[
  {
    "dish_id": "xxx",
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    "difficulty": 1,
    "description": "简单易做的经典家常菜",
    "estimated_time": "15分钟",
    "match_score": 50.0,
    "matched_ingredients": ["番茄", "鸡蛋"]
  },
  {
    "dish_id": "yyy",
    "name": "西兰花炒鸡蛋",
    "category": "素菜",
    "difficulty": 2,
    "description": "营养丰富的蔬菜炒蛋",
    "estimated_time": "20分钟",
    "match_score": 25.0,
    "matched_ingredients": ["鸡蛋"]
  }
]
```

**参数说明**
- `ingredients`: 食材列表（必需）
- `limit`: 返回最多几个推荐（默认 10）

**匹配算法**
- 主料匹配权重为 2，辅料权重为 1
- 最终分数 = (匹配权重 / 总权重) × 100
- 结果按分数降序排列

---

### 4️⃣ 菜品详情

**请求**
```bash
GET /api/v1/dishes/{dish_id}
```

**响应 (200 OK)** - 同 `/random` 端点的完整菜品数据

---

### 5️⃣ 搜索菜品 ⭐ Day 3 新增

**请求**
```bash
# 关键词搜索（支持菜名和描述）
GET /api/v1/dishes/search?q=番茄

# 按分类过滤
GET /api/v1/dishes/search?category=素菜

# 按难度过滤
GET /api/v1/dishes/search?difficulty=1

# 组合条件搜索
GET /api/v1/dishes/search?q=鸡&category=素菜&difficulty=2

# 分页获取
GET /api/v1/dishes/search?skip=0&limit=2

# 完整查询
GET /api/v1/dishes/search?q=番茄&category=素菜&difficulty=1&skip=0&limit=10
```

**参数说明**
| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| q | string | 搜索关键词（可选） | "番茄" |
| category | string | 菜品分类（可选） | "素菜" |
| difficulty | integer | 难度 1-5（可选） | 2 |
| skip | integer | 跳过前 N 条（默认 0） | 0 |
| limit | integer | 返回最多 N 条（默认 10） | 5 |

**响应 (200 OK)**
```json
[
  {
    "id": "xxx",
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    "difficulty": 1,
    "description": "简单易做的经典家常菜",
    "estimated_time": "15分钟",
    "image_url": null,
    "github_url": "https://github.com/Anduin2017/HowToCook",
    "created_at": "2026-02-15T12:00:00"
  },
  {
    "id": "yyy",
    "name": "番茄鸡汤",
    "category": "汤与粥",
    "difficulty": 2,
    "description": "滋补养生的番茄鸡汤",
    "estimated_time": "45分钟",
    "image_url": null,
    "github_url": "https://github.com/Anduin2017/HowToCook",
    "created_at": "2026-02-15T12:00:00"
  }
]
```

**搜索规则**
- 关键词搜索忽略大小写
- 支持模糊匹配（如 "茄" 可匹配 "番茄"）
- 多条件组合使用 AND 逻辑
- 分页从 0 开始计数

---

### 6️⃣ 获取分类列表 ⭐ Day 3 新增

**请求**
```bash
GET /api/v1/categories
```

**响应 (200 OK)**
```json
{
  "categories": ["汤与粥", "素菜"],
  "count": 2
}
```

**用途**: 获取系统中所有菜品分类，用于构建分类过滤菜单

---

### 7️⃣ 获取系统元数据 ⭐ Day 3 新增

**请求**
```bash
GET /api/v1/metadata
```

**响应 (200 OK)**
```json
{
  "total_dishes": 5,
  "categories": ["汤与粥", "素菜"],
  "difficulties": [1, 2, 3, 4, 5],
  "total_ingredients": 14,
  "api_version": "1.0.0"
}
```

**用途**: 获取系统统计信息和配置，用于前端初始化

---

## 🛠️ 常用调用示例（cURL）

### 搜索"番茄"相关菜品

```bash
curl -X GET "http://localhost:8000/api/v1/dishes/search?q=番茄" \
  -H "Content-Type: application/json"
```

### 获取所有"素菜"分类

```bash
curl -X GET "http://localhost:8000/api/v1/dishes/search?category=素菜" \
  -H "Content-Type: application/json"
```

### 获取简单菜品（难度 1 星）

```bash
curl -X GET "http://localhost:8000/api/v1/dishes/search?difficulty=1" \
  -H "Content-Type: application/json"
```

### 推荐菜品（基于食材）

```bash
curl -X POST "http://localhost:8000/api/v1/dishes/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["番茄", "鸡蛋"],
    "limit": 5
  }'
```

### 获取系统信息

```bash
curl -X GET "http://localhost:8000/api/v1/metadata" \
  -H "Content-Type: application/json"
```

---

## ✅ 测试清单

- [x] 健康检查 - 验证服务器状态
- [x] 随机推荐 - 无参数获取随机菜品
- [x] 随机推荐 - 按分类过滤
- [x] 随机推荐 - 按难度过滤
- [x] 食材推荐 - 匹配单个食材
- [x] 食材推荐 - 匹配多个食材
- [x] 菜品详情 - 获取完整信息
- [x] **菜品搜索 - 关键词搜索**
- [x] **菜品搜索 - 分类过滤**
- [x] **菜品搜索 - 难度过滤**
- [x] **菜品搜索 - 组合条件**
- [x] **菜品搜索 - 分页**
- [x] **分类列表 - 获取所有分类**
- [x] **元数据 - 获取系统统计**

---

## 📈 API 端点统计

| 分类 | 数量 | 端点 |
|------|------|------|
| 系统 | 2 | /health, / |
| 菜品查询 | 4 | /random, /recommend, /{id}, /search |
| 元数据 | 2 | /categories, /metadata |
| **总计** | **7** | **8 个端点** |

---

## 🚀 性能提示

1. **搜索性能**: 数据库已在 `Dish.name` 和 `Dish.description` 建立索引
2. **分页建议**: 单次请求 limit ≤ 50
3. **缓存**: 元数据可在前端缓存 1 小时
4. **错误处理**: 所有端点返回错误时的 HTTP 状态码及具体信息

---

## 🔄 下一步

- **Day 4-5**: 开发前端，集成这些 API
- **优化方向**:
  - 添加排序功能（按难度、时间排序）
  - 实现智能搜索（拼音、模糊匹配）
  - 添加菜品收藏功能
