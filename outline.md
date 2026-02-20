# 基于 [HowToCook]([How To Cook](https://cook.aiursoft.com/)) 的菜品生成与查询系统

## 项目需求分析

### 菜品生成

#### 随机生成

- 可选择所有 HowToCook 当中提到过的菜品类别，包括素菜、荤菜、水产、早餐、主食、半成品加工、汤与粥、饮料、酱料和其他材料、甜品，一次能且仅能选择一个类别
- 可选择难度类别，包括 1 星到 5 星，一次能选择 0 到 1 个难度类别
  - **难度覆盖说明**：通过数据爬取和处理，HowToCook 中的所有菜品都有对应的难度标注（在菜谱的"预估烹饪难度"部分标注）。若某菜品未标注难度，默认设置为 3 星（中等难度）
- 根据选定的菜品类别、难度类别，进行菜品随机选取，每次随机选定类别当中一种菜品，可重复操作

#### 半随机生成

基于食材的菜品推荐系统，用户输入食材组合，系统返回可制作的菜品列表。

**问题1：原材料数据提取方案**

从 HowToCook GitHub 仓库的每个菜谱 Markdown 文件中解析"必备原料和工具"部分，提取原料列表。实现步骤：
1. 遍历仓库所有菜谱文件
2. 用正则表达式提取"## 必备原料和工具"与"## 计算"之间的内容
3. 解析原料列表，使用中文分词提取食材名称（去除数量、单位、品牌推荐等修饰词）
4. 构建 `菜品 -> 食材列表` 的映射关系，存储到数据库中

**问题2：给定食材与菜品的对应关系**

采用**模糊匹配 + 多层级筛选**方案：
- **完全匹配**：用户输入的食材集合 ⊆ 菜品食材集合
- **部分匹配**：用户输入的食材与菜品主料中的任意一个匹配（考虑菜品的主要食材权重）
- **模糊匹配**：使用中文分词和编辑距离算法，处理食材名称的近似表述（如"番茄"和"西红柿"）

每次点击"重新生成"，在符合条件的菜品池中随机抽取一个，确保多样性。

**问题3：无符合菜品的处理**

若指定菜品类别 + 难度类别组合中无符合食材要求的菜品，系统返回：
1. **相近难度菜品**：扩大难度范围±1 星，推荐相近难度的符合食材要求的菜品
2. **其他类别菜品**：若无任何难度符合，则跨类别推荐使用相同食材的菜品
3. **友好提示**：显示"当前选择下未找到菜品，已为您推荐相近菜品"

**问题4：任意输入的输出保证**

- **正常食材 + 菜品主料**：直接返回菜品
- **正常食材 + 菜品辅料**：返回使用该食材的菜品（但降低优先级，标记为"可选材料"）
- **正常食材 + 名称不符**：使用分词 + 编辑距离算法进行模糊匹配，例如"西红柿"自动匹配"番茄"
- **非正常食材**：
  - 若不在食材库中且无分词匹配，提示"食材不存在"
  - 若输入是菜品名称，进行智能识别，提示"您输入的是菜品名称，请输入食材"
  - 若输入的是烹饪方式/调料等非食材，提示"请输入食材名称"

**实现建议**：
1. 构建**食材标准库**，包含所有可能的食材变体（如"番茄"、"西红柿"、"华子"等）
2. 使用**分词工具**（如 jieba）进行中文分词处理
3. 对用户输入进行**规范化处理**（去空格、转小写等）
4. 实现**相似度排序**，优先展示匹配度最高的菜品

### 菜品查询

- 生成相应菜品的同时，可点击菜品进入其对应的菜谱页面，类似于超链接
- **搜索引擎模式**：提供全局搜索框，支持按菜品名称、食材、类别、难度进行搜索和筛选，快速定位菜品
- **MCP 集成方案**：搭建 Python/TypeScript MCP 服务器，与 AI 客户端（如 Claude）集成，支持自然语言查询，如"给我推荐一个用番茄的简单菜"


## 数据库

### 数据模型设计

使用 HowToCook 的 GitHub 仓库作为数据库的数据来源，构建以下数据模型：

#### 1. 菜品表 (Dish)
```
{
  id: string (菜品唯一标识)
  name: string (菜品名称，如"番茄炒蛋")
  category: string (类别：素菜|荤菜|水产|早餐|主食|半成品加工|汤与粥|饮料|酱料和其他材料|甜品)
  difficulty: integer (难度：1-5 星，默认3)
  description: string (菜品简介)
  estimated_time: string (预估制作时间，如"15 分钟")
  image_url: string (成品图片链接，可选)
  github_url: string (GitHub 仓库原链接)
  ingredients: [string] (食材ID列表，外键)
  main_ingredients: [string] (主料ID列表，用于权重计算)
  steps: [object] (步骤列表，参考下面的步骤表)
  created_at: timestamp
  updated_at: timestamp
}
```

#### 2. 食材表 (Ingredient)
```
{
  id: string (食材唯一标识)
  name: string (标准食材名称)
  aliases: [string] (别名列表，如"番茄": ["西红柿", "华子"])
  category: string (食材分类：蔬菜|肉类|水产|水果|调料|其他)
  normalized_name: string (规范化名称，用于模糊匹配，如去除繁简转换后的结果)
}
```

#### 3. 步骤表 (CookingStep)
```
{
  id: string
  dish_id: string (外键)
  step_number: integer (步骤序号)
  description: string (步骤描述)
  duration: string (预估耗时，如"10 分钟"，可选)
}
```

#### 4. 菜品-食材关联表 (DishIngredient)
```
{
  id: string
  dish_id: string (外键)
  ingredient_id: string (外键)
  quantity: string (数量描述，如"2个", "100g")
  is_main: boolean (是否为主料)
  is_optional: boolean (是否为可选)
}
```

### 数据来源与处理流程

1. **数据爬取**：Clone HowToCook GitHub 仓库，遍历所有 Markdown 菜谱文件
2. **数据解析**：
   - 菜品名称：从文件名或标题提取
   - 类别：通过目录结构判断（如 `素菜/菠菜.md`）
   - 难度：从"预估烹饪难度"部分用正则表达式提取星级数
   - 食材：从"必备原料和工具"部分解析，去除数量和品牌信息
   - 步骤：从"操作"部分逐行解析
3. **食材规范化**：
   - 使用中文分词工具 (jieba) 提取食材核心词汇
   - 构建食材别名库，合并重复或相似的食材
   - 生成规范化名称用于模糊匹配
4. **数据存储**：导入到数据库（详见后端章节）

### 数据质量保证

- 定期更新 HowToCook 仓库数据
- 人工审验新增菜品的食材解析准确性
- 维护食材别名库的完整性



## 前后端

> 先实现后端，再实现前端，最后实现前后端交互。用 demo 的形式展示每个阶段的功能。

## 前后端

### 后端

#### 技术栈选型

- **语言**：Python 3.9+ (使用 FastAPI 框架，因为需要处理复杂的分词和匹配逻辑)
- **数据库**：SQLite（开发/演示阶段）或 PostgreSQL（生产环境）
- **核心库**：
  - `FastAPI` / `Starlette`：Web 框架
  - `SQLAlchemy`：ORM 框架
  - `jieba`：中文分词
  - `difflib` / `Levenshtein`：编辑距离计算（食材模糊匹配）
  - `PyGithub`：GitHub API 调用（仓库数据爬取）
  - `python-dotenv`：环境变量管理

#### 项目结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置文件
│   ├── database.py             # 数据库连接和会话
│   ├── models/
│   │   ├── __init__.py
│   │   ├── dish.py             # 菜品数据模型
│   │   ├── ingredient.py       # 食材数据模型
│   │   └── cooking_step.py     # 步骤数据模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── dish.py             # 菜品请求/响应 Pydantic 模型
│   │   └── ingredient.py       # 食材请求/响应 Pydantic 模型
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── dishes.py       # 菜品相关 API 端点
│   │   │   ├── ingredients.py  # 食材相关 API 端点
│   │   │   ├── search.py       # 搜索和推荐 API 端点
│   │   │   └── random.py       # 随机生成 API 端点
│   ├── services/
│   │   ├── __init__.py
│   │   ├── dish_service.py     # 菜品业务逻辑
│   │   ├── ingredient_service.py # 食材业务逻辑
│   │   ├── matcher.py          # 食材匹配引擎
│   │   └── scraper.py          # GitHub 数据爬取
│   └── utils/
│       ├── __init__.py
│       ├── tokenizer.py        # 分词工具
│       ├── similarity.py       # 相似度计算
│       └── constants.py        # 常量定义
├── tests/                      # 单元测试
├── requirements.txt            # 依赖列表
├── .env.example                # 环境变量模板
└── README.md
```

#### 核心 API 端点设计

**1. 随机生成菜品**
- `GET /api/v1/random`
- 参数：`category` (可选), `difficulty` (可选)
- 响应：单个菜品完整信息
- 逻辑：根据条件筛选菜品池，随机抽取一个

**2. 基于食材推荐**
- `POST /api/v1/recommend`
- 请求体：`{ "ingredients": ["番茄", "鸡蛋"], "category": "素菜", "difficulty": 3 }`
- 响应：符合条件的菜品列表（按匹配度排序）
- 逻辑：使用食材匹配引擎进行模糊匹配和排序

**3. 搜索菜品**
- `GET /api/v1/search`
- 参数：`q` (搜索关键词), `category` (可选), `difficulty` (可选)
- 响应：菜品列表
- 逻辑：全文搜索菜品名称、描述、食材等字段

**4. 获取菜品详情**
- `GET /api/v1/dishes/{dish_id}`
- 响应：菜品完整信息（包括步骤、食材等）

**5. 获取所有食材**
- `GET /api/v1/ingredients`
- 响应：食材列表（用于前端下拉框填充）

**6. 获取菜品类别和难度列表**
- `GET /api/v1/metadata`
- 响应：`{ "categories": [...], "difficulties": [1,2,3,4,5] }`

#### 食材匹配引擎核心算法

```python
# 伪代码
def match_ingredients(user_inputs, all_dishes):
    """
    返回按匹配度排序的菜品列表
    匹配度计算规则：
    1. 完全匹配（用户所有食材都在菜品主料中）：权重 100
    2. 主料部分匹配（用户至少一个食材在菜品主料中）：权重 80
    3. 任意匹配（用户至少一个食材在菜品食材中）：权重 60
    4. 模糊匹配（食材名称相似度 > 阈值）：权重 40
    5. 无匹配：权重 0（过滤掉）
    """
    results = []
    
    for dish in all_dishes:
        score = 0
        
        for user_input in user_inputs:
            normalized_input = normalize(user_input)
            
            # 尝试完全匹配
            if match_in_list(normalized_input, dish.main_ingredients):
                score = max(score, 100)
            # 尝试主料匹配
            elif match_in_list(normalized_input, dish.ingredients):
                score = max(score, 80)
            # 尝试模糊匹配
            else:
                max_similarity = max([
                    similarity(normalized_input, normalize(ing))
                    for ing in dish.ingredients
                ])
                if max_similarity > THRESHOLD:
                    score = max(score, 40 + max_similarity * 40)
        
        if score > 0:
            results.append((dish, score))
    
    return sorted(results, key=lambda x: x[1], reverse=True)
```

#### 初始化和部署步骤

1. 创建虚拟环境并安装依赖
2. 配置环境变量（数据库 URL、GitHub Token 等）
3. 运行数据爬取和初始化脚本
4. 创建数据库表结构（SQLAlchemy 迁移）
5. 启动 FastAPI 开发服务器：`uvicorn app.main:app --reload`


### 前端

#### 技术栈选型

- **框架**：React 18 + TypeScript (使用 Vite 作为构建工具，提升开发体验)
- **UI 库**：Ant Design (antd) 或 Material-UI (MUI)（拥有丰富的组件库）
- **HTTP 客户端**：axios 或 fetch API
- **状态管理**：Zustand 或 React Query（轻量级选项，避免过度工程化）
- **样式**：Tailwind CSS + CSS Modules

#### 项目结构
```
frontend/
├── src/
│   ├── components/
│   │   ├── RandomDish.tsx       # 随机生成菜品组件
│   │   ├── IngredientSelector.tsx # 食材选择器（半随机生成）
│   │   ├── SearchBar.tsx        # 搜索框组件
│   │   ├── DishCard.tsx         # 菜品卡片组件
│   │   ├── DishDetail.tsx       # 菜品详情模态框
│   │   └── RecipeViewer.tsx     # 菜谱查看器
│   ├── pages/
│   │   ├── Home.tsx             # 主页/首页
│   │   ├── SearchResults.tsx    # 搜索结果页
│   │   └── About.tsx            # 关于页面
│   ├── services/
│   │   └── api.ts               # API 调用封装
│   ├── hooks/
│   │   ├── useDish.ts           # 菜品数据 hook
│   │   ├── useSearch.ts         # 搜索 hook
│   │   └── useRandom.ts         # 随机生成 hook
│   ├── types/
│   │   ├── dish.ts              # 菜品类型定义
│   │   └── ingredient.ts        # 食材类型定义
│   ├── utils/
│   │   └── helpers.ts           # 工具函数
│   ├── styles/
│   │   ├── global.css           # 全局样式
│   │   └── theme.ts             # 主题配置
│   ├── App.tsx
│   └── main.tsx
├── public/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

#### 主要页面和交互设计

**1. 主页（Home Page）**
- 上方：导航栏（包含logo、搜索框、导航链接）
- 中上：大标题和应用简介
- 中间：两个主要操作区域
  - 左侧：随机生成区域
    - 类别下拉框（可选）
    - 难度滑块（可选，1-5星）
    - "随机推荐"按钮
    - 显示生成的菜品卡片（含菜品名称、图片、难度、时间）
    - 点击菜品可查看详情或查看菜谱
  - 右侧：基于食材区域
    - 食材输入框 + "添加"按钮
    - 已选食材标签列表（可删除）
    - 类别下拉框（可选）
    - 难度滑块（可选）
    - "开始推荐"按钮
    - 推荐结果（菜品卡片列表）
- 下方：页脚（包含项目信息、数据来源等）

**2. 搜索结果页（SearchResults Page）**
- 搜索框（显示当前搜索词，可修改）
- 筛选条件（类别、难度、排序方式）
- 结果列表（使用分页或无限滚动）
- 点击菜品进入详情页

**3. 菜品详情模态框/页面**
- 菜品名称和基本信息（类别、难度、预估时间）
- 菜品成品图片
- 菜品描述和营养价值
- "必备原料和工具"表格
- "计算"部分（份数计算器）
- "操作"步骤（可视化步骤列表，每个步骤可展开/收起）
- "附加内容"注意事项
- "返回"或"查看原菜谱"按钮（链接到 GitHub）

#### 前端工作流和交互逻辑

**随机生成流程**
```
用户选择类别(可选) + 难度(可选) 
  → 点击"随机推荐"
  → 调用 GET /api/v1/random API
  → 显示菜品卡片
  → 用户可点击卡片查看详情或点击"重新生成"
```

**基于食材推荐流程**
```
用户输入食材1 → 点击"+"添加食材2 → ... → 选择类别(可选) + 难度(可选)
  → 点击"开始推荐"
  → 调用 POST /api/v1/recommend API
  → 显示排序后的菜品列表
  → 用户点击菜品卡片查看详情
  → 若无结果，显示友好提示并建议修改条件
```

**搜索流程**
```
用户在搜索框输入关键词
  → 支持实时搜索建议（可选，需要防抖）
  → 按 Enter 或点击搜索按钮
  → 跳转到搜索结果页
  → 调用 GET /api/v1/search API
  → 显示结果列表
```

#### 前端部署和开发流程

1. 创建 Vite + React + TypeScript 项目：`npm create vite@latest frontend -- --template react-ts`
2. 安装依赖：`npm install`
3. 配置 API 基础 URL（通过环境变量）
4. 开发模式：`npm run dev`
5. 生产构建：`npm run build`
6. 部署：将 `dist` 文件夹上传到静态托管服务（如 Vercel、GitHub Pages、Netlify 等）


### 前后端交互

#### API 规范

所有 API 基础 URL：`http://localhost:8000/api/v1` (开发环境)

**通用响应格式**
```json
{
  "code": 200,          // HTTP 状态码
  "message": "success", // 响应消息
  "data": {},           // 响应数据
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**错误响应格式**
```json
{
  "code": 400,
  "message": "Invalid ingredients",
  "errors": ["Food X is not in the ingredient database"]
}
```

#### 详细 API 端点规范

**1. 随机获取菜品**

```
GET /api/v1/dishes/random

Query Parameters:
  - category: string (可选，如 "素菜", "荤菜" 等)
  - difficulty: integer (可选，1-5)

Response:
{
  "code": 200,
  "data": {
    "id": "broccoli_egg",
    "name": "西兰花炒鸡蛋",
    "category": "素菜",
    "difficulty": 2,
    "description": "简单易做的家常菜",
    "estimated_time": "15 分钟",
    "image_url": "https://...",
    "ingredients": [
      { "id": "broccoli", "name": "西兰花", "quantity": "200g" },
      { "id": "egg", "name": "鸡蛋", "quantity": "2个" }
    ],
    "steps": [
      {
        "step_number": 1,
        "description": "西兰花切小朵，鸡蛋打散",
        "duration": "3 分钟"
      },
      ...
    ]
  }
}
```

**2. 基于食材推荐菜品**

```
POST /api/v1/dishes/recommend

Request Body:
{
  "ingredients": ["番茄", "鸡蛋"],
  "category": "素菜",        // 可选
  "difficulty": 3,           // 可选
  "limit": 10                // 可选，返回结果数量
}

Response:
{
  "code": 200,
  "data": [
    {
      "id": "tomato_egg",
      "name": "番茄炒鸡蛋",
      "category": "素菜",
      "difficulty": 1,
      "match_score": 100,     // 匹配度（0-100）
      "matched_ingredients": ["番茄", "鸡蛋"],
      "image_url": "https://...",
      "description": "经典家常菜"
    },
    ...
  ]
}

Error Case:
{
  "code": 400,
  "message": "No matching dishes found",
  "data": {
    "suggestions": [
      { "name": "番茄鸡汤", "reason": "Uses similar ingredients" }
    ]
  }
}
```

**3. 搜索菜品**

```
GET /api/v1/dishes/search

Query Parameters:
  - q: string (必需，搜索关键词)
  - category: string (可选)
  - difficulty: integer (可选)
  - sort_by: string (可选，如 "relevance", "difficulty", "time")
  - page: integer (可选，默认1)
  - page_size: integer (可选，默认10)

Response:
{
  "code": 200,
  "data": {
    "total": 25,
    "page": 1,
    "page_size": 10,
    "items": [
      {
        "id": "tomato_egg",
        "name": "番茄炒鸡蛋",
        "category": "素菜",
        "difficulty": 1,
        "image_url": "https://...",
        "description": "经典家常菜"
      },
      ...
    ]
  }
}
```

**4. 获取菜品详情**

```
GET /api/v1/dishes/{dish_id}

Response:
{
  "code": 200,
  "data": {
    "id": "tomato_egg",
    "name": "番茄炒鸡蛋",
    "category": "素菜",
    "difficulty": 1,
    "description": "经典家常菜，富含蛋白质和维生素",
    "estimated_time": "15 分钟",
    "image_url": "https://...",
    "github_url": "https://github.com/Anduin2017/HowToCook/blob/master/...",
    "ingredients": [
      {
        "id": "tomato",
        "name": "番茄",
        "quantity": "2个",
        "is_main": true,
        "is_optional": false
      },
      {
        "id": "egg",
        "name": "鸡蛋",
        "quantity": "3个",
        "is_main": true,
        "is_optional": false
      },
      {
        "id": "oil",
        "name": "食用油",
        "quantity": "15ml",
        "is_main": false,
        "is_optional": false
      }
    ],
    "steps": [
      {
        "step_number": 1,
        "description": "番茄切块，鸡蛋打散",
        "duration": "2 分钟"
      },
      {
        "step_number": 2,
        "description": "热锅下油，炒鸡蛋至半熟",
        "duration": "3 分钟"
      },
      ...
    ],
    "notes": "需要注意不要炒过头，保持鸡蛋的嫩度"
  }
}
```

**5. 获取所有食材（用于前端自动完成）**

```
GET /api/v1/ingredients

Query Parameters:
  - prefix: string (可选，用于自动完成)

Response:
{
  "code": 200,
  "data": [
    {
      "id": "tomato",
      "name": "番茄",
      "aliases": ["西红柿", "华子"],
      "category": "蔬菜"
    },
    ...
  ]
}
```

**6. 获取元数据（类别、难度等）**

```
GET /api/v1/metadata

Response:
{
  "code": 200,
  "data": {
    "categories": [
      { "id": "vegetable", "name": "素菜" },
      { "id": "meat", "name": "荤菜" },
      ...
    ],
    "difficulties": [
      { "level": 1, "label": "简单" },
      { "level": 2, "label": "容易" },
      { "level": 3, "label": "中等" },
      { "level": 4, "label": "困难" },
      { "level": 5, "label": "极难" }
    ]
  }
}
```

#### 前后端数据流示意图

```
前端流程                          后端处理                        数据库查询
------                           ------                          -----

【随机生成】
用户选择条件
    ↓
GET /random
    ├─────────────────→ 解析参数
    │                    ↓
    │              根据条件过滤菜品池
    │                    ↓
    │              从池中随机抽取
    │                    ↓
    │              查询菜品详情 ─→ SELECT FROM dishes...
    │                    ↓
    ←────────────── 返回菜品数据
    ↓
显示菜品卡片


【基于食材推荐】
用户输入食材
    ↓
POST /recommend
    ├─────────────────→ 食材规范化处理
    │                    ↓
    │              查询所有符合条件的菜品 ─→ SELECT FROM dishes...
    │                    ↓              JOIN ingredients...
    │              执行匹配算法
    │                    ↓
    │              计算匹配度和排序
    │                    ↓
    ←────────────── 返回排序后的列表
    ↓
显示推荐结果


【搜索菜品】
用户输入关键词
    ↓
GET /search
    ├─────────────────→ 全文搜索
    │                    ↓
    │              查询匹配的菜品 ─→ SELECT FROM dishes...
    │                    WHERE name LIKE...
    │                    ↓
    │              应用排序和分页
    │                    ↓
    ←────────────── 返回搜索结果
    ↓
显示结果列表
```

#### 前端调用示例（TypeScript）

```typescript
// services/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const dishAPI = {
  getRandom: (category?: string, difficulty?: number) =>
    axios.get(`${API_BASE_URL}/dishes/random`, {
      params: { category, difficulty }
    }),

  getRecommendations: (ingredients: string[], category?: string, difficulty?: number) =>
    axios.post(`${API_BASE_URL}/dishes/recommend`, {
      ingredients,
      category,
      difficulty
    }),

  search: (query: string, category?: string, difficulty?: number) =>
    axios.get(`${API_BASE_URL}/dishes/search`, {
      params: { q: query, category, difficulty }
    }),

  getDetail: (dishId: string) =>
    axios.get(`${API_BASE_URL}/dishes/${dishId}`),

  getIngredients: (prefix?: string) =>
    axios.get(`${API_BASE_URL}/ingredients`, {
      params: { prefix }
    })
};

// 在 React 组件中使用
const { data } = await dishAPI.getRandom('素菜', 2);
console.log(data.data); // 菜品信息
```

## 项目部署与维护

## 7-9 天加速计划详细执行指南

### 第 1 天：环境配置 + 数据爬取（重要！）

**时间**：4-8 小时  
**目标**：成功爬取 HowToCook 数据，建立完整的 SQLite 数据库

**任务清单**：
- [ ] 初始化 Git 仓库和项目结构
  ```bash
  mkdir SearchMenu && cd SearchMenu
  git init
  mkdir backend frontend
  ```
  
- [ ] 创建后端虚拟环境
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```

- [ ] 创建 `requirements.txt` 并安装依赖
  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  sqlalchemy==2.0.23
  pydantic==2.5.0
  jieba==0.42.1
  python-dotenv==1.0.0
  requests==2.31.0
  ```

- [ ] 创建数据库模型文件 (`models.py`)
  - Dish 表、Ingredient 表、CookingStep 表

- [ ] 编写 GitHub 爬取脚本 (`scripts/scraper.py`)
  - Clone HowToCook 仓库（或直接读取已有内容）
  - 解析 Markdown 文件
  - 提取菜品名、类别、难度、食材、步骤
  - 使用 jieba 分词提取食材核心词汇

- [ ] 运行爬取脚本，导入数据到 SQLite
  ```bash
  python scripts/init_db.py  # 初始化数据库
  python scripts/scraper.py  # 爬取数据
  ```

- [ ] 验证数据
  ```bash
  # 使用 SQLite 客户端检查数据
  sqlite3 search_menu.db "SELECT COUNT(*) FROM dishes;"
  ```

**成功标志**：
✓ `search_menu.db` 文件存在  
✓ 数据库中有 50+ 个菜品  
✓ 每个菜品都有食材和步骤  
✓ 食材表中有规范化的食材名称和别名

**如遇问题**：
- 若爬取失败，可从 JSON 或 CSV 文件导入预处理的数据（节省时间）
- 数据不完整可先用 20-30 个菜品启动，后续补充

---

### 第 2 天：后端核心 API（FastAPI 项目）

**时间**：4-8 小时  
**目标**：实现 2 个核心 API 并通过测试

**任务清单**：
- [ ] 创建 FastAPI 应用主文件 (`app/main.py`)
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  app = FastAPI(title="SearchMenu API")
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"],
  )
  
  @app.get("/api/v1/health")
  async def health():
      return {"status": "ok"}
  ```

- [ ] 创建数据库连接模块 (`app/database.py`)

- [ ] 实现随机生成 API
  ```python
  @app.get("/api/v1/dishes/random")
  async def random_dish(category: str = None, difficulty: int = None):
      # 根据条件筛选，随机返回一个菜品
      pass
  ```

- [ ] 实现推荐 API（核心算法）
  ```python
  @app.post("/api/v1/dishes/recommend")
  async def recommend_dishes(request: RecommendRequest):
      # 1. 规范化食材输入
      # 2. 执行匹配算法
      # 3. 按匹配度排序返回
      pass
  ```

- [ ] 创建 Pydantic 请求/响应模型 (`app/schemas.py`)

- [ ] 编写食材匹配引擎 (`app/services/matcher.py`)
  - 实现 `match_ingredients()` 函数
  - 支持完全匹配、部分匹配、模糊匹配

- [ ] 测试 API
  ```bash
  uvicorn app.main:app --reload
  # 访问 http://localhost:8000/docs 查看 Swagger 文档
  ```

**代码模板**：
```python
# app/services/matcher.py
def normalize_ingredient(ingredient: str) -> str:
    """规范化食材名称"""
    return ingredient.strip().lower()

def match_ingredients(user_inputs: list[str], dish_id: str, db) -> int:
    """
    计算匹配度分数 (0-100)
    完全匹配 = 100
    主料匹配 = 80
    模糊匹配 = 40-60
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        return 0
    
    score = 0
    for user_input in user_inputs:
        normalized = normalize_ingredient(user_input)
        
        # 检查主料
        if any(normalized in ing.name.lower() 
               for ing in dish.main_ingredients):
            score = max(score, 100)
        # 检查所有食材
        elif any(normalized in ing.name.lower() 
                 for ing in dish.ingredients):
            score = max(score, 80)
    
    return score
```

**成功标志**：
✓ 可以访问 `http://localhost:8000/docs`  
✓ `/dishes/random` 可返回一个菜品  
✓ `/dishes/recommend` 可接收食材并返回推荐列表  
✓ 返回的数据结构正确

---

### 第 3 天：完善后端 API

**时间**：4-8 小时  
**目标**：实现所有 5 个主要 API，使后端功能完整

**任务清单**：
- [ ] 实现搜索 API
  ```python
  @app.get("/api/v1/dishes/search")
  async def search_dishes(q: str, category: str = None, 
                         difficulty: int = None, page: int = 1):
      # 全文搜索：菜品名称、描述、食材
      # 支持筛选和分页
      pass
  ```

- [ ] 实现菜品详情 API
  ```python
  @app.get("/api/v1/dishes/{dish_id}")
  async def get_dish_detail(dish_id: str):
      # 返回菜品的完整信息（包括步骤和食材详情）
      pass
  ```

- [ ] 实现食材列表 API
  ```python
  @app.get("/api/v1/ingredients")
  async def list_ingredients(prefix: str = None):
      # 用于前端自动完成
      # 可选参数：按前缀过滤
      pass
  ```

- [ ] 实现元数据 API
  ```python
  @app.get("/api/v1/metadata")
  async def get_metadata():
      # 返回所有类别、难度等信息
      return {
          "categories": [...],
          "difficulties": [1, 2, 3, 4, 5]
      }
  ```

- [ ] 完善错误处理和验证
  ```python
  from fastapi import HTTPException
  
  @app.exception_handler(ValueError)
  async def value_error_handler(request, exc):
      return JSONResponse(
          status_code=400,
          content={"code": 400, "message": str(exc)}
      )
  ```

- [ ] 添加日志和调试
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info(f"Fetching random dish with: {category}, {difficulty}")
  ```

- [ ] 测试所有 API 端点
  - 使用 curl 或 Postman 测试每个端点
  - 验证响应格式和错误处理

**测试示例**：
```bash
# 测试随机生成
curl http://localhost:8000/api/v1/dishes/random

# 测试推荐
curl -X POST http://localhost:8000/api/v1/dishes/recommend \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["番茄", "鸡蛋"]}'

# 测试搜索
curl "http://localhost:8000/api/v1/dishes/search?q=番茄"
```

**成功标志**：
✓ 所有 5 个 API 都能正常返回数据  
✓ 错误情况下返回适当的错误信息  
✓ Swagger 文档显示所有端点  
✓ 后端可以保持运行而不崩溃

---

### 第 4 天：前端基础 + 连接 API

**时间**：4-8 小时  
**目标**：创建可用的前端，实现随机生成和推荐功能

**任务清单**：
- [ ] 初始化前端项目（使用 Vanilla JS 而不是 React，加速开发）
  ```bash
  cd frontend
  npm init -y
  npm install -D vite tailwindcss autoprefixer axios
  npx tailwindcss init -p
  ```

- [ ] 创建基础 HTML 结构 (`index.html`)
  ```html
  <!DOCTYPE html>
  <html lang="zh-CN">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>SearchMenu - 菜品查询系统</title>
      <link rel="stylesheet" href="/src/styles.css">
  </head>
  <body>
      <div id="app">
          <!-- 导航栏 -->
          <nav class="navbar">
              <h1>🍳 SearchMenu</h1>
          </nav>
          
          <!-- 主容器 -->
          <main class="container">
              <!-- 随机生成区域 -->
              <section id="random-section" class="section">
                  <h2>随机推荐</h2>
                  <div class="controls">
                      <select id="category-select">
                          <option value="">所有类别</option>
                      </select>
                      <input type="range" id="difficulty-slider" min="0" max="5" value="0">
                      <button id="random-btn">随机推荐</button>
                  </div>
                  <div id="random-result" class="result"></div>
              </section>
              
              <!-- 基于食材区域 -->
              <section id="ingredient-section" class="section">
                  <h2>基于食材推荐</h2>
                  <div class="ingredient-input">
                      <input type="text" id="ingredient-input" 
                             placeholder="输入食材名称（如番茄）">
                      <button id="ingredient-add-btn">添加</button>
                  </div>
                  <div id="selected-ingredients" class="tags"></div>
                  <button id="recommend-btn">推荐菜品</button>
                  <div id="recommend-result" class="result-list"></div>
              </section>
          </main>
      </div>
      
      <script type="module" src="/src/main.js"></script>
  </body>
  </html>
  ```

- [ ] 创建 API 客户端 (`src/api.js`)
  ```javascript
  const API_BASE = 'http://localhost:8000/api/v1';
  
  export const api = {
      getRandom: (category, difficulty) =>
          fetch(`${API_BASE}/dishes/random?category=${category}&difficulty=${difficulty}`)
              .then(r => r.json()),
      
      getRecommendations: (ingredients) =>
          fetch(`${API_BASE}/dishes/recommend`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ ingredients })
          }).then(r => r.json()),
      
      getDishDetail: (dishId) =>
          fetch(`${API_BASE}/dishes/${dishId}`)
              .then(r => r.json()),
      
      search: (query) =>
          fetch(`${API_BASE}/dishes/search?q=${query}`)
              .then(r => r.json()),
      
      getMetadata: () =>
          fetch(`${API_BASE}/metadata`)
              .then(r => r.json())
  };
  ```

- [ ] 创建主应用逻辑 (`src/main.js`)
  ```javascript
  import { api } from './api.js';
  
  let selectedIngredients = [];
  
  // 初始化
  document.addEventListener('DOMContentLoaded', async () => {
      const metadata = await api.getMetadata();
      populateCategorySelect(metadata.categories);
  });
  
  // 随机推荐按钮
  document.getElementById('random-btn').addEventListener('click', async () => {
      const category = document.getElementById('category-select').value;
      const difficulty = document.getElementById('difficulty-slider').value || null;
      
      const result = await api.getRandom(category, difficulty);
      displayDishResult(result.data, 'random-result');
  });
  
  // 添加食材按钮
  document.getElementById('ingredient-add-btn').addEventListener('click', () => {
      const input = document.getElementById('ingredient-input');
      const ingredient = input.value.trim();
      
      if (ingredient && !selectedIngredients.includes(ingredient)) {
          selectedIngredients.push(ingredient);
          renderSelectedIngredients();
          input.value = '';
      }
  });
  
  // 推荐按钮
  document.getElementById('recommend-btn').addEventListener('click', async () => {
      const result = await api.getRecommendations(selectedIngredients);
      displayDishList(result.data, 'recommend-result');
  });
  
  function displayDishResult(dish, elementId) {
      const html = `
          <div class="dish-card">
              <h3>${dish.name}</h3>
              <p>难度：${'⭐'.repeat(dish.difficulty)}</p>
              <p>时间：${dish.estimated_time}</p>
              <button onclick="viewDetail('${dish.id}')">查看详情</button>
          </div>
      `;
      document.getElementById(elementId).innerHTML = html;
  }
  
  function displayDishList(dishes, elementId) {
      const html = dishes.map(dish => `
          <div class="dish-card">
              <h3>${dish.name}</h3>
              <p>匹配度：${dish.match_score}%</p>
              <button onclick="viewDetail('${dish.id}')">查看详情</button>
          </div>
      `).join('');
      document.getElementById(elementId).innerHTML = html;
  }
  
  function renderSelectedIngredients() {
      const container = document.getElementById('selected-ingredients');
      container.innerHTML = selectedIngredients.map(ing => `
          <span class="tag">
              ${ing}
              <button onclick="removeIngredient('${ing}')">✕</button>
          </span>
      `).join('');
  }
  ```

- [ ] 创建基础样式 (`src/styles.css`)
  ```css
  * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
  }
  
  body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
  }
  
  .navbar {
      background: #fff;
      padding: 1rem 2rem;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  
  .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
  }
  
  .section {
      background: #fff;
      padding: 2rem;
      margin-bottom: 2rem;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  .controls, .dish-card {
      display: flex;
      gap: 1rem;
      margin: 1rem 0;
  }
  
  button {
      padding: 0.5rem 1rem;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
  }
  
  button:hover {
      background: #2563eb;
  }
  
  .tags {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
      margin: 1rem 0;
  }
  
  .tag {
      background: #dbeafe;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
  }
  ```

- [ ] 测试前端连接
  ```bash
  npm run dev
  # 访问 http://localhost:5173
  ```

**成功标志**：
✓ 前端可以访问  
✓ 点击"随机推荐"可以显示菜品  
✓ 添加食材后点击推荐可以显示列表  
✓ 前后端 CORS 没有问题  
✓ 控制台没有错误

---

### 第 5 天：搜索页面 + 菜品详情

**时间**：4-8 小时  
**目标**：完整的用户交互流程

**任务清单**：
- [ ] 添加搜索功能到首页导航栏
- [ ] 创建菜品详情模态框
  ```javascript
  async function viewDetail(dishId) {
      const result = await api.getDishDetail(dishId);
      const dish = result.data;
      
      const modal = `
          <div class="modal">
              <div class="modal-content">
                  <span class="close-btn">&times;</span>
                  <h2>${dish.name}</h2>
                  <p>${dish.description}</p>
                  <h3>必备原料</h3>
                  <ul>
                      ${dish.ingredients.map(ing => 
                          `<li>${ing.name} - ${ing.quantity}</li>`
                      ).join('')}
                  </ul>
                  <h3>操作步骤</h3>
                  <ol>
                      ${dish.steps.map(step => 
                          `<li>${step.description}</li>`
                      ).join('')}
                  </ol>
                  <a href="${dish.github_url}" target="_blank">查看原菜谱</a>
              </div>
          </div>
      `;
      document.body.insertAdjacentHTML('beforeend', modal);
      document.querySelector('.close-btn').onclick = () => 
          document.querySelector('.modal').remove();
  }
  ```

- [ ] 创建搜索结果页面
  ```javascript
  async function performSearch(query) {
      const result = await api.search(query);
      displayDishList(result.data.items, 'search-results');
  }
  ```

- [ ] 优化移动端响应式设计
- [ ] 添加 loading 状态
  ```javascript
  function showLoading(elementId) {
      document.getElementById(elementId).innerHTML = 
          '<p class="loading">加载中...</p>';
  }
  ```

- [ ] 添加错误处理和提示

**成功标志**：
✓ 可以搜索菜品  
✓ 可以查看菜品详情  
✓ 移动端可用  
✓ 响应式布局正常

---

### 第 6 天：调试 + 优化

**时间**：4-8 小时  
**目标**：应用可稳定运行，用户体验良好

**任务清单**：
- [ ] 完整的端到端测试流程
  - [ ] 测试随机生成 5 次
  - [ ] 测试推荐各种组合的食材
  - [ ] 测试搜索功能
  - [ ] 测试菜品详情加载

- [ ] Bug 修复
  - [ ] 检查控制台错误
  - [ ] 处理 API 超时情况
  - [ ] 处理空结果情况

- [ ] 性能优化
  - [ ] 添加结果缓存（localStorage）
  - [ ] 图片懒加载（如有）
  - [ ] 减少不必要的 API 调用

- [ ] 用户体验改进
  - [ ] 添加 Loading 状态
  - [ ] 改进错误提示信息
  - [ ] 美化 UI 细节
  - [ ] 添加键盘快捷键支持

- [ ] 文档更新
  - [ ] 编写 README（安装、运行、使用说明）
  - [ ] 记录已知的 bug 或限制

**成功标志**：
✓ 应用可以正常使用  
✓ 没有明显的 bug  
✓ 性能可接受（API 响应 < 500ms）  
✓ 用户体验流畅

---

### 第 7-9 天（可选）：部署 + 扩展功能

**时间**：4-8 小时 × 3 天  
**目标**：应用上线部署，准备展示

**第 7 天：部署后端**
- [ ] 创建 Docker 镜像
- [ ] 部署到 Railway 或 Render（10 分钟免费部署）
- [ ] 配置生产环境变量
- [ ] 验证部署成功

**第 8 天：部署前端**
- [ ] 构建前端项目 `npm run build`
- [ ] 部署到 Vercel（支持 GitHub 自动部署）
- [ ] 配置生产环境 API URL
- [ ] 验证部署成功

**第 9 天：扩展功能（可选）**
- [ ] 添加收藏夹功能（localStorage）
- [ ] 优化搜索建议（本地缓存）
- [ ] 添加主题切换（深色模式）
- [ ] 制作项目演示视频

---

## 完整的 7-9 天时间表总结

| 天数 | 重点 | 工作量 | 复杂度 | 产出 |
|------|------|--------|--------|------|
| 第 1 天 | 数据准备 | 4-8h | 中 | SQLite DB + 50+ 菜品 |
| 第 2 天 | 后端 API #1 | 4-8h | 中 | /random + /recommend 可用 |
| 第 3 天 | 后端 API #2-5 | 4-8h | 中 | 所有 API 完成 |
| 第 4 天 | 前端 + 集成 | 4-8h | 中 | 基础功能可用 |
| 第 5 天 | 搜索 + 详情 | 4-8h | 低 | 完整用户流程 |
| 第 6 天 | 调试 + 优化 | 4-8h | 低 | 稳定版本 |
| 第 7-9 天 | 部署 + 扩展 | 4-8h | 低 | 上线可用 |

**总工作量**：28-72 小时（充分覆盖）

---

## 立即执行步骤（现在就做！）

### 第 0 步：准备工作（今天，30-60 分钟）

**目标**：搭建开发环境，确保所有必要工具就绪

**检查清单**：
- [ ] 确认已安装 Python 3.9+ 和 pip
  ```bash
  python --version
  pip --version
  ```

- [ ] 确认已安装 Git
  ```bash
  git --version
  ```

- [ ] 确认已安装 Node.js 16+ 和 npm
  ```bash
  node --version
  npm --version
  ```

- [ ] 创建项目根目录
  ```bash
  mkdir SearchMenu && cd SearchMenu
  git init
  echo "# SearchMenu - 菜品生成与查询系统" > README.md
  git add README.md && git commit -m "Initial commit"
  ```

- [ ] 创建项目结构
  ```bash
  mkdir backend frontend
  mkdir -p backend/app/services backend/scripts
  mkdir -p frontend/src/{api,styles}
  ```

- [ ] 创建 `.gitignore` 文件
  ```bash
  cat > .gitignore << 'EOF'
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  venv/
  env/
  *.db
  .env
  
  # Node
  node_modules/
  dist/
  .env.local
  
  # IDE
  .vscode/
  .idea/
  *.swp
  EOF
  ```

**完成后**：项目文件夹结构清晰，可以开始编码

---

### 第 1 步：快速启动后端数据库（第 1 天，2-3 小时）

**目标**：创建 SQLite 数据库和基础数据模型

**逐行执行**：

1️⃣ **创建虚拟环境**
```bash
cd backend
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

2️⃣ **创建 `requirements.txt`**
```bash
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
jieba==0.42.1
python-dotenv==1.0.0
requests==2.31.0
EOF

pip install -r requirements.txt
```

3️⃣ **创建数据库模型** (`app/models.py`)
```bash
cat > app/models.py << 'EOF'
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Dish(Base):
    __tablename__ = "dishes"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    difficulty = Column(Integer, default=3)
    description = Column(Text)
    estimated_time = Column(String)
    image_url = Column(String)
    github_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ingredients = relationship("DishIngredient", back_populates="dish")
    steps = relationship("CookingStep", back_populates="dish")

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    aliases = Column(String)  # JSON 字符串，逗号分隔
    category = Column(String)  # 蔬菜, 肉类, 水产等
    normalized_name = Column(String, index=True)
    
    dish_ingredients = relationship("DishIngredient", back_populates="ingredient")

class DishIngredient(Base):
    __tablename__ = "dish_ingredients"
    
    id = Column(String, primary_key=True)
    dish_id = Column(String, ForeignKey("dishes.id"), index=True)
    ingredient_id = Column(String, ForeignKey("ingredients.id"), index=True)
    quantity = Column(String)
    is_main = Column(Boolean, default=False)
    is_optional = Column(Boolean, default=False)
    
    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dish_ingredients")

class CookingStep(Base):
    __tablename__ = "cooking_steps"
    
    id = Column(String, primary_key=True)
    dish_id = Column(String, ForeignKey("dishes.id"), index=True)
    step_number = Column(Integer)
    description = Column(Text)
    duration = Column(String)
    
    dish = relationship("Dish", back_populates="steps")
EOF
```

4️⃣ **创建数据库初始化脚本** (`app/database.py`)
```bash
cat > app/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

DATABASE_URL = "sqlite:///./search_menu.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
```

5️⃣ **创建初始化脚本** (`scripts/init_db.py`)
```bash
cat > scripts/init_db.py << 'EOF'
import sys
sys.path.insert(0, '..')

from app.database import init_db, SessionLocal
from app.models import Dish, Ingredient, DishIngredient, CookingStep
import json
import uuid

# 初始化数据库表
init_db()
print("✓ 数据库表创建成功")

# 创建示例数据
db = SessionLocal()

# 示例菜品数据
sample_dishes = [
    {
        "name": "番茄炒鸡蛋",
        "category": "素菜",
        "difficulty": 1,
        "description": "简单易做的经典家常菜",
        "estimated_time": "15分钟",
        "ingredients": ["番茄", "鸡蛋"],
        "main_ingredients": ["番茄", "鸡蛋"]
    },
    {
        "name": "西兰花炒鸡蛋",
        "category": "素菜",
        "difficulty": 2,
        "description": "营养丰富的蔬菜炒蛋",
        "estimated_time": "20分钟",
        "ingredients": ["西兰花", "鸡蛋", "油盐"],
        "main_ingredients": ["西兰花", "鸡蛋"]
    },
    {
        "name": "番茄鸡汤",
        "category": "汤与粥",
        "difficulty": 2,
        "description": "滋补养生的番茄鸡汤",
        "estimated_time": "45分钟",
        "ingredients": ["番茄", "鸡肉", "水", "盐"],
        "main_ingredients": ["番茄", "鸡肉"]
    }
]

for dish_data in sample_dishes:
    dish = Dish(
        id=str(uuid.uuid4()),
        name=dish_data["name"],
        category=dish_data["category"],
        difficulty=dish_data["difficulty"],
        description=dish_data["description"],
        estimated_time=dish_data["estimated_time"],
        github_url=f"https://github.com/Anduin2017/HowToCook"
    )
    db.add(dish)
    db.flush()
    
    # 添加食材
    for ing_name in dish_data["ingredients"]:
        ingredient = db.query(Ingredient).filter(
            Ingredient.name == ing_name
        ).first()
        
        if not ingredient:
            ingredient = Ingredient(
                id=str(uuid.uuid4()),
                name=ing_name,
                normalized_name=ing_name.lower()
            )
            db.add(ingredient)
            db.flush()
        
        is_main = ing_name in dish_data["main_ingredients"]
        dish_ing = DishIngredient(
            id=str(uuid.uuid4()),
            dish_id=dish.id,
            ingredient_id=ingredient.id,
            quantity="适量",
            is_main=is_main
        )
        db.add(dish_ing)

db.commit()
print("✓ 示例数据导入成功")
db.close()

print("\n数据库初始化完成！")
print("下一步：python scripts/init_db.py")
EOF

python scripts/init_db.py
```

6️⃣ **验证数据库创建**
```bash
# 检查数据库文件
ls -lh search_menu.db

# 验证表
sqlite3 search_menu.db ".tables"

# 查看菜品数量
sqlite3 search_menu.db "SELECT COUNT(*) FROM dishes;"
```

✅ **成功标志**：
- `search_menu.db` 文件存在
- SQLite 中有 `dishes`、`ingredients` 等表
- 有至少 3 个示例菜品

---

### 第 2 步：实现第一个 API（第 2 天，2-3 小时）

**目标**：让 FastAPI 服务器运行，实现随机生成和推荐 API

1️⃣ **创建主应用** (`app/main.py`)
```bash
cat > app/main.py << 'EOF'
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
import json

from app.database import get_db, init_db
from app.models import Dish, Ingredient, DishIngredient
from pydantic import BaseModel

app = FastAPI(title="SearchMenu API", version="1.0")

# CORS 配置（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup():
    init_db()

# ========== Pydantic 模型 ==========
class IngredientSchema(BaseModel):
    id: str
    name: str
    quantity: str = None
    is_main: bool = False

class StepSchema(BaseModel):
    step_number: int
    description: str
    duration: str = None

class DishSchema(BaseModel):
    id: str
    name: str
    category: str
    difficulty: int
    description: str = None
    estimated_time: str = None
    ingredients: list[IngredientSchema] = []
    steps: list[StepSchema] = []

class RecommendRequest(BaseModel):
    ingredients: list[str]
    category: str = None
    difficulty: int = None

# ========== API 端点 ==========

@app.get("/api/v1/health")
async def health():
    """健康检查"""
    return {"status": "ok"}

@app.get("/api/v1/metadata")
async def get_metadata(db: Session = Depends(get_db)):
    """获取菜品类别和难度列表"""
    categories = db.query(
        Dish.category
    ).distinct().all()
    
    return {
        "code": 200,
        "data": {
            "categories": [{"id": cat[0], "name": cat[0]} 
                          for cat in categories],
            "difficulties": [
                {"level": i, "label": ["极简", "简单", "容易", "中等", "困难"][i]}
                for i in range(1, 6)
            ]
        }
    }

@app.get("/api/v1/dishes/random")
async def random_dish(
    category: str = None,
    difficulty: int = None,
    db: Session = Depends(get_db)
):
    """随机获取一道菜品"""
    query = db.query(Dish)
    
    if category:
        query = query.filter(Dish.category == category)
    if difficulty:
        query = query.filter(Dish.difficulty == difficulty)
    
    count = query.count()
    if count == 0:
        raise HTTPException(status_code=404, 
                          detail="没有符合条件的菜品")
    
    offset = random.randint(0, count - 1)
    dish = query.offset(offset).first()
    
    # 获取食材和步骤
    ingredients = [
        IngredientSchema(
            id=di.ingredient.id,
            name=di.ingredient.name,
            quantity=di.quantity,
            is_main=di.is_main
        )
        for di in dish.ingredients
    ]
    
    steps = [
        StepSchema(
            step_number=s.step_number,
            description=s.description,
            duration=s.duration
        )
        for s in dish.steps
    ]
    
    return {
        "code": 200,
        "data": DishSchema(
            id=dish.id,
            name=dish.name,
            category=dish.category,
            difficulty=dish.difficulty,
            description=dish.description,
            estimated_time=dish.estimated_time,
            ingredients=ingredients,
            steps=steps
        ).dict()
    }

@app.post("/api/v1/dishes/recommend")
async def recommend_dishes(
    request: RecommendRequest,
    db: Session = Depends(get_db)
):
    """基于食材推荐菜品"""
    if not request.ingredients:
        raise HTTPException(status_code=400, 
                          detail="请提供至少一个食材")
    
    # 规范化用户输入
    user_ingredients = [ing.lower().strip() 
                       for ing in request.ingredients]
    
    # 查询所有菜品
    query = db.query(Dish)
    if request.category:
        query = query.filter(Dish.category == request.category)
    if request.difficulty:
        query = query.filter(Dish.difficulty == request.difficulty)
    
    dishes = query.all()
    
    # 匹配评分
    results = []
    for dish in dishes:
        score = 0
        matched_ingredients = []
        
        for user_ing in user_ingredients:
            for di in dish.ingredients:
                dish_ing_name = di.ingredient.name.lower()
                
                # 完全匹配
                if user_ing in dish_ing_name or \
                   dish_ing_name in user_ing:
                    score = max(score, 100 if di.is_main else 80)
                    matched_ingredients.append(di.ingredient.name)
                    break
        
        if score > 0:
            results.append({
                "dish": dish,
                "score": score,
                "matched": matched_ingredients
            })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 构建响应
    data = [
        {
            "id": r["dish"].id,
            "name": r["dish"].name,
            "category": r["dish"].category,
            "difficulty": r["dish"].difficulty,
            "match_score": r["score"],
            "matched_ingredients": r["matched"],
            "description": r["dish"].description
        }
        for r in results[:10]  # 返回前 10 个
    ]
    
    if not data:
        return {
            "code": 200,
            "data": [],
            "message": "没有找到匹配的菜品"
        }
    
    return {
        "code": 200,
        "data": data
    }

@app.get("/api/v1/dishes/{dish_id}")
async def get_dish_detail(
    dish_id: str,
    db: Session = Depends(get_db)
):
    """获取菜品详情"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    
    if not dish:
        raise HTTPException(status_code=404, 
                          detail="菜品不存在")
    
    ingredients = [
        IngredientSchema(
            id=di.ingredient.id,
            name=di.ingredient.name,
            quantity=di.quantity,
            is_main=di.is_main
        )
        for di in dish.ingredients
    ]
    
    steps = [
        StepSchema(
            step_number=s.step_number,
            description=s.description,
            duration=s.duration
        )
        for s in sorted(dish.steps, key=lambda x: x.step_number)
    ]
    
    return {
        "code": 200,
        "data": {
            "id": dish.id,
            "name": dish.name,
            "category": dish.category,
            "difficulty": dish.difficulty,
            "description": dish.description,
            "estimated_time": dish.estimated_time,
            "github_url": dish.github_url,
            "ingredients": [ing.dict() for ing in ingredients],
            "steps": [step.dict() for step in steps]
        }
    }

@app.get("/api/v1/ingredients")
async def list_ingredients(
    prefix: str = None,
    db: Session = Depends(get_db)
):
    """获取所有食材（用于自动完成）"""
    query = db.query(Ingredient).order_by(Ingredient.name)
    
    if prefix:
        query = query.filter(
            Ingredient.name.ilike(f"%{prefix}%")
        )
    
    ingredients = query.limit(50).all()
    
    return {
        "code": 200,
        "data": [
            {
                "id": ing.id,
                "name": ing.name,
                "aliases": ing.aliases.split(",") if ing.aliases else []
            }
            for ing in ingredients
        ]
    }

@app.get("/api/v1/dishes/search")
async def search_dishes(
    q: str,
    category: str = None,
    difficulty: int = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """搜索菜品"""
    if not q:
        raise HTTPException(status_code=400, 
                          detail="请提供搜索关键词")
    
    query = db.query(Dish).filter(
        Dish.name.ilike(f"%{q}%") | 
        Dish.description.ilike(f"%{q}%")
    )
    
    if category:
        query = query.filter(Dish.category == category)
    if difficulty:
        query = query.filter(Dish.difficulty == difficulty)
    
    total = query.count()
    
    dishes = query.limit(page_size).offset(
        (page - 1) * page_size
    ).all()
    
    return {
        "code": 200,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": d.id,
                    "name": d.name,
                    "category": d.category,
                    "difficulty": d.difficulty,
                    "description": d.description
                }
                for d in dishes
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
```

2️⃣ **创建空的 `__init__.py`**
```bash
touch app/__init__.py
touch app/services/__init__.py
```

3️⃣ **启动服务器**
```bash
uvicorn app.main:app --reload
```

4️⃣ **验证 API**
```bash
# 在新终端中测试
curl http://localhost:8000/api/v1/health

curl http://localhost:8000/api/v1/dishes/random

curl -X POST http://localhost:8000/api/v1/dishes/recommend \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["番茄"]}'
```

5️⃣ **查看 API 文档**
访问 http://localhost:8000/docs （Swagger UI）

✅ **成功标志**：
- 服务器启动成功，无报错
- `/health` 返回 `{"status": "ok"}`
- `/dishes/random` 返回一道菜品
- `/dishes/recommend` 可以推荐菜品
- Swagger 文档可以访问

---

### 第 3 步：创建前端并连接 API（第 3-4 天，4-6 小时）

**目标**：简单可用的前端，能与后端 API 通信

1️⃣ **创建前端项目**
```bash
cd frontend
npm init -y
npm install -D vite axios
npm install tailwindcss postcss autoprefixer

# 初始化 Tailwind
npx tailwindcss init -p
```

2️⃣ **创建 `index.html`**
```bash
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SearchMenu - 菜品查询系统</title>
    <link rel="stylesheet" href="/src/styles.css">
</head>
<body class="bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow">
        <div class="container mx-auto px-4 py-4">
            <h1 class="text-2xl font-bold text-blue-600">🍳 SearchMenu</h1>
        </div>
    </nav>

    <!-- 主容器 -->
    <main class="container mx-auto px-4 py-8">
        <!-- 随机推荐区域 -->
        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">🎲 随机推荐</h2>
            <div class="flex gap-4 mb-4 flex-wrap">
                <select id="category-select" class="px-4 py-2 border rounded">
                    <option value="">所有类别</option>
                    <option value="素菜">素菜</option>
                    <option value="荤菜">荤菜</option>
                    <option value="汤与粥">汤与粥</option>
                </select>
                <button id="random-btn" class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    推荐一道菜
                </button>
            </div>
            <div id="random-result"></div>
        </section>

        <!-- 基于食材区域 -->
        <section class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold mb-4">🥘 基于食材推荐</h2>
            <div class="flex gap-2 mb-4">
                <input type="text" id="ingredient-input" 
                       placeholder="输入食材名称（如番茄）"
                       class="flex-1 px-4 py-2 border rounded"
                       onkeypress="handleKeyPress(event)">
                <button id="ingredient-add-btn" class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                    添加
                </button>
            </div>
            <div id="selected-ingredients" class="flex flex-wrap gap-2 mb-4"></div>
            <button id="recommend-btn" class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-4">
                开始推荐
            </button>
            <div id="recommend-result"></div>
        </section>
    </main>

    <script type="module" src="/src/main.js"></script>
</body>
</html>
EOF
```

3️⃣ **创建 API 客户端** (`src/api.js`)
```bash
mkdir -p src
cat > src/api.js << 'EOF'
const API_BASE = 'http://localhost:8000/api/v1';

export const api = {
    getRandom: async (category, difficulty) => {
        let url = `${API_BASE}/dishes/random`;
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (difficulty && difficulty > 0) params.append('difficulty', difficulty);
        if (params.toString()) url += '?' + params.toString();
        
        const res = await fetch(url);
        return res.json();
    },
    
    getRecommendations: async (ingredients) => {
        const res = await fetch(`${API_BASE}/dishes/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ingredients })
        });
        return res.json();
    },
    
    getDishDetail: async (dishId) => {
        const res = await fetch(`${API_BASE}/dishes/${dishId}`);
        return res.json();
    },
    
    search: async (query) => {
        const res = await fetch(`${API_BASE}/dishes/search?q=${encodeURIComponent(query)}`);
        return res.json();
    },
    
    getMetadata: async () => {
        const res = await fetch(`${API_BASE}/metadata`);
        return res.json();
    }
};
EOF
```

4️⃣ **创建主应用** (`src/main.js`)
```bash
cat > src/main.js << 'EOF'
import { api } from './api.js';

let selectedIngredients = [];

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    // 加载类别
    const metadata = await api.getMetadata();
    const select = document.getElementById('category-select');
    for (const cat of metadata.data.categories) {
        const option = document.createElement('option');
        option.value = cat.id;
        option.textContent = cat.name;
        select.appendChild(option);
    }
});

// 随机推荐
document.getElementById('random-btn').addEventListener('click', async () => {
    const category = document.getElementById('category-select').value;
    const result = await api.getRandom(category);
    
    if (result.data) {
        displayDish(result.data, 'random-result');
    } else {
        document.getElementById('random-result').innerHTML = 
            '<p class="text-red-500">没有符合条件的菜品</p>';
    }
});

// 添加食材
document.getElementById('ingredient-add-btn').addEventListener('click', addIngredient);

// 推荐菜品
document.getElementById('recommend-btn').addEventListener('click', async () => {
    if (selectedIngredients.length === 0) {
        alert('请先添加食材');
        return;
    }
    
    const result = await api.getRecommendations(selectedIngredients);
    
    if (result.data && result.data.length > 0) {
        displayDishList(result.data, 'recommend-result');
    } else {
        document.getElementById('recommend-result').innerHTML = 
            '<p class="text-red-500">没有找到匹配的菜品，请尝试其他食材</p>';
    }
});

function addIngredient() {
    const input = document.getElementById('ingredient-input');
    const ing = input.value.trim();
    
    if (ing && !selectedIngredients.includes(ing)) {
        selectedIngredients.push(ing);
        renderIngredients();
        input.value = '';
    }
}

function removeIngredient(ing) {
    selectedIngredients = selectedIngredients.filter(i => i !== ing);
    renderIngredients();
}

function renderIngredients() {
    const container = document.getElementById('selected-ingredients');
    container.innerHTML = selectedIngredients.map(ing => `
        <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full flex items-center gap-2">
            ${ing}
            <button onclick="removeIngredient('${ing}')" class="font-bold">✕</button>
        </span>
    `).join('');
}

function displayDish(dish, elementId) {
    const html = `
        <div class="bg-gray-100 p-6 rounded-lg">
            <h3 class="text-2xl font-bold mb-2">${dish.name}</h3>
            <p class="text-gray-600 mb-2">${dish.description || '暂无描述'}</p>
            <div class="flex gap-4 mb-4 text-sm text-gray-600">
                <span>⭐ 难度：${dish.difficulty}/5</span>
                <span>⏱️ ${dish.estimated_time || '未知'}</span>
                <span>🏷️ ${dish.category}</span>
            </div>
            <button onclick="viewDetail('${dish.id}')" 
                    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                查看详情
            </button>
        </div>
    `;
    document.getElementById(elementId).innerHTML = html;
}

function displayDishList(dishes, elementId) {
    const html = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${dishes.map(d => `
                <div class="bg-gray-100 p-4 rounded-lg">
                    <h4 class="font-bold text-lg mb-2">${d.name}</h4>
                    <p class="text-sm text-gray-600 mb-2">匹配度：${d.match_score}%</p>
                    <p class="text-sm mb-2">⭐ ${d.difficulty}/5</p>
                    <button onclick="viewDetail('${d.id}')" 
                            class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                        详情
                    </button>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById(elementId).innerHTML = html;
}

async function viewDetail(dishId) {
    const result = await api.getDishDetail(dishId);
    const dish = result.data;
    
    const modal = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
                    <h2 class="text-2xl font-bold">${dish.name}</h2>
                    <button onclick="this.closest('.fixed').remove()" class="text-2xl">✕</button>
                </div>
                <div class="p-6">
                    <p class="text-gray-600 mb-4">${dish.description || '暂无描述'}</p>
                    
                    <h3 class="text-lg font-bold mb-2">必备原料</h3>
                    <ul class="list-disc pl-5 mb-4">
                        ${dish.ingredients.map(ing => `
                            <li>${ing.name} - ${ing.quantity || '适量'}</li>
                        `).join('')}
                    </ul>
                    
                    <h3 class="text-lg font-bold mb-2">操作步骤</h3>
                    <ol class="list-decimal pl-5 mb-4">
                        ${dish.steps.map(step => `
                            <li class="mb-2">${step.description}</li>
                        `).join('')}
                    </ol>
                    
                    ${dish.github_url ? `
                        <a href="${dish.github_url}" target="_blank" 
                           class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
                            查看原菜谱
                        </a>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modal);
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        addIngredient();
    }
}

// 暴露全局函数
window.removeIngredient = removeIngredient;
window.viewDetail = viewDetail;
window.handleKeyPress = handleKeyPress;
EOF
```

5️⃣ **创建样式文件** (`src/styles.css`)
```bash
cat > src/styles.css << 'EOF'
@import url('https://cdn.tailwindcss.com');

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
EOF
```

6️⃣ **更新 `package.json`**
```bash
cat > package.json << 'EOF'
{
  "name": "search-menu-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.0"
  },
  "dependencies": {
    "axios": "^1.6.2"
  }
}
EOF

npm install
```

7️⃣ **启动前端开发服务器**
```bash
npm run dev
# 访问 http://localhost:5173
```

✅ **成功标志**：
- 前端页面可以访问
- 点击"推荐一道菜"可以显示菜品
- 可以添加食材并推荐
- 可以查看菜品详情

---

## 完整命令复制（快速开始）

**如果你想快速复制所有命令，按顺序运行**：

```bash
# 步骤 0：环境准备
mkdir SearchMenu && cd SearchMenu
git init

# 步骤 1：后端数据库
cd backend
python -m venv venv
source venv/bin/activate  # 或 Windows: venv\Scripts\activate

cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
jieba==0.42.1
python-dotenv==1.0.0
requests==2.31.0
EOF

pip install -r requirements.txt

# ... （复制上面的 models.py, database.py, main.py 等）

# 步骤 2：启动后端
uvicorn app.main:app --reload

# 新终端：步骤 3：前端
cd frontend
npm init -y && npm install -D vite axios tailwindcss postcss autoprefixer
npx tailwindcss init -p

# ... （复制上面的 HTML, JS, CSS 等）

npm run dev
```

---

## 现在就开始！

### 📋 你现在的待办清单：

**今天立即做**：
1. [ ] 创建项目目录和 Git 仓库（10 分钟）
2. [ ] 设置后端虚拟环境（5 分钟）
3. [ ] 创建数据库模型和初始化脚本（30 分钟）
4. [ ] 导入示例数据（10 分钟）
5. [ ] 创建 FastAPI 主应用（60 分钟）
6. [ ] 启动后端服务器并测试（15 分钟）

**明天做**：
1. [ ] 初始化前端项目（10 分钟）
2. [ ] 创建 HTML + CSS（30 分钟）
3. [ ] 创建 API 客户端（20 分钟）
4. [ ] 连接前后端（30 分钟）
5. [ ] 测试完整流程（10 分钟）

---

## 遇到问题快速排查

| 问题 | 解决方案 |
|------|--------|
| Python 版本太低 | `python --version` 升级到 3.9+ |
| 虚拟环境无法激活 | 检查路径，或直接用 `pip install` 到系统 |
| 端口 8000 被占用 | `uvicorn app.main:app --port 8001` |
| CORS 错误 | 确保后端配置了 CORS 中间件 |
| 前端无法连接后端 | 检查后端是否在运行，API 地址是否正确 |
| 数据库找不到菜品 | 检查 `init_db.py` 是否成功运行 |

**需要帮助？**
- 任何一步卡住，告诉我具体的错误信息
- 我会帮你调试

祝你开发顺利！🚀

### 打包与部署

#### 后端部署

**本地开发**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # 在 Windows 上为 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 运行开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Docker 部署（推荐）**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建和运行 Docker 镜像
docker build -t search-menu-backend .
docker run -d -p 8000:8000 --name search-menu-api search-menu-backend
```

**云平台部署选项**
- **Heroku** (简单，免费套餐有限制)
  ```bash
  heroku create search-menu-api
  git push heroku main
  ```
- **Railway / Render** (现代替代品，支持自动部署)
- **AWS / Google Cloud / Azure** (生产级，需配置)

#### 前端部署

**本地开发**
```bash
# 安装依赖
npm install

# 开发服务器
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

**静态托管部署**

选项 1：Vercel (推荐，与 Vite 兼容性最好)
```bash
# 全局安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

选项 2：GitHub Pages
```bash
# 在 vite.config.ts 中设置
export default {
  base: '/SearchMenu/',
  // ...
}

# 构建并部署
npm run build
git add dist/
git commit -m "Deploy"
git push
```

选项 3：Netlify
```bash
# 连接 GitHub 仓库后，Netlify 会自动构建和部署
# 配置文件：netlify.toml
[build]
  command = "npm run build"
  publish = "dist"
```

#### 环境变量配置

**后端 (.env)**
```env
# 数据库
DATABASE_URL=sqlite:///./search_menu.db
# 或 PostgreSQL: postgresql://user:password@localhost/dbname

# GitHub API (数据爬取)
GITHUB_TOKEN=your_github_token_here

# 应用配置
DEBUG=True
SECRET_KEY=your_secret_key_here
```

**前端 (.env.local)**
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
# 生产环境
VITE_API_URL=https://api.yourdomain.com/api/v1
```

### 维护与更新

**定期任务**

1. **每周**：数据同步
   - 运行脚本检查 HowToCook GitHub 仓库是否有新菜品
   - 如有更新，自动爬取并导入数据库
   ```bash
   python scripts/sync_recipes.py
   ```

2. **每月**：数据质量审验
   - 检查食材别名库的完整性
   - 验证菜品分类和难度标注
   - 处理用户反馈的数据问题

3. **每季度**：性能优化和功能迭代
   - 分析用户使用数据（搜索热词、推荐效果等）
   - 优化匹配算法准确度
   - 添加新功能（如收藏夹、用户评分等）

**监控和告警**
- 后端 API 可用性监控 (如使用 Sentry 追踪错误)
- 数据库性能监控 (如 pg_stat_statements)
- 前端错误日志收集 (如 Sentry、LogRocket)
- 设置告警阈值，当 API 响应时间 > 500ms 或错误率 > 1% 时通知

**版本管理**
- 使用 Git 进行版本控制，采用 Git Flow 工作流
- 前后端各自维护 CHANGELOG.md 记录版本变更
- 使用 Semantic Versioning (x.y.z) 进行版本号管理

**备份和恢复**
- 每日自动备份数据库文件
- 保留至少 30 天的备份历史
- 定期测试恢复流程确保可用性

### 项目文档

**应生成的文档清单**
1. `README.md` - 项目介绍、快速开始、功能演示
2. `CONTRIBUTING.md` - 贡献指南、代码规范
3. `API_DOCS.md` - API 文档（包含所有端点、参数、响应示例）
4. `DEPLOYMENT.md` - 详细部署指南（本地、Docker、云平台）
5. `DATABASE_SCHEMA.md` - 数据库表结构和关系图
6. `ARCHITECTURE.md` - 系统架构设计和技术决策记录
7. `TROUBLESHOOTING.md` - 常见问题和解决方案



## 附录

### 项目实施路线图（甘特图）

```
周期        阶段1           阶段2           阶段3           阶段4           阶段5
          后端基础         后端核心        前端基础        前后集成        测试部署
          (1-2周)         (3-4周)         (5-6周)         (7-8周)         (9-10周)

任务1 ────────────────────
  数据库模型和爬取脚本

任务2           ────────────────────
  食材匹配引擎和搜索功能

任务3                       ──────────────────────
  前端 UI 和组件开发

任务4                                   ────────────────────
  API 集成和优化

任务5                                           ──────────────────
  测试和部署

[完成时间点]
第 2 周末 → 后端基础完成，可开始前端平行开发
第 4 周末 → 后端全部功能完成
第 6 周末 → 前端 UI 完成
第 8 周末 → 前后端集成完成，可开始 UAT
第 10 周末 → 项目正式上线
```

### 快速开始指南

**准备环境**
- Python 3.9+
- Node.js 16+ 和 npm 8+
- Git
- （可选）Docker

**克隆和初始化后端**
```bash
git clone <repository-url>
cd backend

# 安装依赖
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 运行后端
uvicorn app.main:app --reload
```

**克隆和初始化前端**
```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev
```

**访问应用**
- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 技术决策记录 (ADR)

| 决策 | 选择 | 原因 |
|------|------|------|
| 后端框架 | FastAPI | 异步支持、自动 API 文档、类型检查 |
| 前端框架 | React 18 | 生态成熟、学习资源丰富、社区活跃 |
| 数据库 | SQLite(开发) + PostgreSQL(生产) | 轻量级开发、可扩展性好 |
| 分词工具 | jieba | 中文分词效果好、使用广泛 |
| UI 组件库 | Ant Design | 企业级设计系统、组件丰富 |
| 构建工具 | Vite | 快速冷启动、热模块替换、现代化 |
| 部署方式 | Docker + 云平台 | 可复现、易于扩展、便于 CI/CD |

### 可参考的衍生作品

- [图像化菜谱：支持在线预览与 PDF 导出](https://king-jingxiang.github.io/HowToCook/)
- [HowToCook-mcp 让 AI 助手变身私人大厨，为你的一日三餐出谋划策](https://github.com/worryzyy/HowToCook-mcp)
- [HowToCook-py-mcp 让 AI 助手变身私人大厨，为你的一日三餐出谋划策 (Python)](https://github.com/DusKing1/howtocook-py-mcp)
- [whatToEat 今天吃什么？的决策工具，帮助你快速选择合适的菜谱。](https://github.com/ryanuo/whatToEat)

### 示例菜谱格式
```markdown
<!-- 这是 HowToCook 菜谱仓库中的示例菜谱模板文件。 -->
<!-- 注意：在编写时，中文与英文或数字之间必须有且仅有一个空格。 -->
<!-- 注意：在编写时，标题与正文之间必须有且仅有一个空行。 -->

# 示例菜的做法

<!-- 标题必须是 `菜名` + `的做法`。和文件名一致。 -->

<!-- 如果有图片更好。 -->

![示例菜成品](./示例菜.jpg)

<!-- 在这里简单介绍菜的特点、营养价值、难度、预计制作时长。 -->
示例菜是一道简单易做的菜。富含 DHA 和蛋白质。一般初学者只需要 3 小时即可完成。还有美容效果哦~

<!--
1星：没有特别困难的步骤。只需要将原材料简单混合烹饪即可。大约5分钟即可完成。即使没有做饭经验的人，也可以按照步骤做出像模像样的效果。
2星：包含的步骤非常简单。不太需要烹饪经验，只需要按照步骤进行操作即可。大约10分钟即可完成。即使没有做饭经验的人，也可以按照步骤做出像模像样的效果，但是想要做出完美的效果就需要一定的练习。
3星：包含的步骤不算太复杂。需要一定烹饪经验，能够熟练掌握火候、时间、材料组合的技巧。大约15分钟即可完成。对于有经验的厨师，并不会太难，但是想要做出完美的效果也需要一定的经验加上练习。
4星：包含了很多复杂的步骤。需要精妙的掌握火候、时间、材料组合的技巧。40分钟以内即可完成。即使是有经验的厨师，也需要花费很多时间来准备这道菜，但是做熟练之后，就可以做出非常美味的效果。
5星：包含了很多复杂的步骤。需要精妙的掌握火候、时间、材料组合的技巧。可能需要40分钟以上才能完成。即使是有经验的厨师，也需要花费很多时间来准备这道菜，并且非常容易出现失误。
-->

预估烹饪难度：★★★★

## 必备原料和工具

<!-- 在这里列出必需原料。以方便大家快速判断自己手边的材料是否足够。-->

<!-- 注意：某些原料已经在厨房采购部分提及。这里不要重复提及： -->
<!-- 燃气灶, 饮用水, 锅, 食用油, 碗与盘子, 筷子, 炒勺, 洗涤剂, 抹布, 钢丝球, 菜刀 -->

<!-- 可以推荐购买哪个品牌的来方便决策。 -->

- 咖喱块（推荐品牌好侍）
- 土豆
- 藤椒油（可选）

## 计算

<!-- 这一章节里介绍一些计算公式，求得原料的量、重要的时间参数、混合比例，以便在后续操作中引用。 -->

<!-- 这里有两种情况： -->
<!-- 1. 可能会大批量做菜。例如：食堂给全校学生做西红柿鸡蛋、米饭、米粥。这种情况需要给出计算公式。 -->
<!-- 2. 固定菜量的产品菜。每份的容量一致而永远不会发生变化。这种情况需要给出一份的量。 -->

每次制作前需要确定计划做几份。一份正好够 2 个人吃。

每份：

<!-- 对于大小不一的食材，必须给出质量参考 -->
<!-- 对于可以自行斟酌加量的食材，必须给出建议添加的范围 -->
<!-- 请不要使用有大有小的容器作为单位！这会令人困惑，难以后续精准化。请使用毫升！ -->

- 咖喱块 115g
- 土豆 2 个（每个土豆大约重 120g，共约 240g）
- 食用油 10-15ml

## 操作

<!-- 在这里详细描述做菜的全部流程。 -->
<!-- 不允许使用不精准描述的词汇，例如：`适 量`、`少 量`、`中 量`、`适 当`。 -->
<!-- 在这里，如果操作的食材不是“全部食材”而是“部分食材”，也必须指明。否则默认指定的是全部原料。例如这里‘土豆’表示‘全部准备好的土豆’。 -->

- 土豆去皮、切成不超过 4cm 的大块，备用
- 咖喱块切碎，增加接触面积加速溶解，备用
- 热锅，锅内放入 10ml - 15ml 食用油。等待 10 秒让油温升高
- 放入土豆，保持翻炒至土豆*变软*（可以用筷子确认）<!-- 在描述过程时不得加入上文或原材料中未提及的食材。 -->
- 加水没过所有食材，沸腾后，将火调小然后**等待 15 - 20 分钟** <!-- 对于可以自行斟酌加量的食材，必须给出建议的范围 -->
- 关火，加咖喱并搅拌，等待直至咖喱融化 <!-- 凡是需要等待的步骤必须给出`等待时间计算公式`或`结束一个步骤的判断标准` -->
- 再开火，缓慢**搅拌 10 分钟**，防止糊锅
- 在外观*呈粘稠状态*后关火，盛盘

## 附加内容

<!-- 在这里额外补充一些注意事项、参考资料、安全须知等。 -->

- 操作时，需要注意观察沸腾的水位线，如发现低于 2/3 的食材应加热水至没过食材。
- 参考资料：[世界美食教程的微博视频](http://t.cn/EJ77yFy)

<!-- 必须保留下面的文字。 -->
如果您遵循本指南的制作流程而发现有问题或可以改进的流程，请提出 Issue 或 Pull request 。

<!-- 在提交 Pull Request 前，请删除模板中的所有注释。 -->
```



