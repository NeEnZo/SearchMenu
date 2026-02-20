# 🚀 Day 4-5 前端开发完整指南

## ✅ 前端项目初始化完成

### 📁 项目结构
```
/mnt/c/SearchMenu/frontend/
├── src/
│   ├── main.js              ✅ 主应用逻辑（600+ 行）
│   ├── api.js               ✅ API 客户端封装
│   └── styles.css           ✅ Tailwind CSS 样式
├── index.html               ✅ 主页面（交互式）
├── vite.config.js           ✅ Vite 配置
├── tailwind.config.js       ✅ Tailwind 配置
├── postcss.config.js        ✅ PostCSS 配置
├── package.json             ✅ 项目配置
└── run.sh                   ✅ 快速启动脚本
```

---

## 🎯 核心功能已实现

### 1️⃣ **主页面功能**
- ✅ 菜品搜索（支持关键词）
- ✅ 分类过滤
- ✅ 难度过滤
- ✅ 菜品网格展示
- ✅ 分页功能
- ✅ 随机推荐
- ✅ 基于食材推荐
- ✅ 模态框详情展示

### 2️⃣ **API 集成**
- ✅ 全 7 个 API 端点集成
- ✅ Axios 自动拦截器
- ✅ 错误处理
- ✅ 加载指示器

### 3️⃣ **UI/UX 特性**
- ✅ 响应式设计（Tailwind CSS）
- ✅ 现代化界面
- ✅ 平滑动画过渡
- ✅ 深色背景梯度
- ✅ 卡片悬停效果
- ✅ 加载状态提示

---

## 🚀 启动前端开发

### 方式 1：使用启动脚本（推荐）
```bash
cd /mnt/c/SearchMenu/frontend
bash run.sh
```

### 方式 2：直接使用 npm
```bash
cd /mnt/c/SearchMenu/frontend
npm install     # 首次运行
npm run dev     # 启动开发服务器
```

### 方式 3：使用 Vite CLI
```bash
cd /mnt/c/SearchMenu/frontend
npx vite
```

**输出示例：**
```
  VITE v6.4.1  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

---

## 🌐 访问前端应用

打开浏览器访问：
```
http://localhost:5173
```

或者 Vite 会自动打开浏览器。

---

## 📋 前端功能详解

### 页面布局

```
┌─────────────────────────────────────────────────────┐
│  🍽️ SearchMenu - AI 菜品搜索平台                   │
│  ✨ AI 驱动的菜品搜索和食材推荐平台                 │
├─────────────────────────────────────────────────────┤
│  🔍 搜索栏 │ 🏷️ 分类 │ ⭐ 难度 │ 🔎 搜索按钮     │
├─────────────────────────────────────────────────────┤
│  🎲 随机推荐 │ 💡 基于食材推荐                     │
├─────────────────────────────────────────────────────┤
│  🥘 基于食材推荐                                   │
│  [食材输入框] [添加] 按钮                           │
│  [已添加的食材标签] [✕] [✕] ...                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  📋 菜品列表                                        │
│  ┌──────────────┐  ┌──────────────┐              │
│  │ 番茄炒鸡蛋   │  │ 西兰花炒鸡蛋│ ...           │
│  │ 素菜 ⭐      │  │ 素菜 ⭐⭐   │              │
│  └──────────────┘  └──────────────┘              │
│                                                     │
│  ← 上一页 [1] [2] [3] 下一页 →                    │
└─────────────────────────────────────────────────────┘
```

### 核心交互流程

```
1. 用户搜索/过滤菜品
   ↓
2. 前端调用 API (GET /api/v1/dishes/search)
   ↓
3. 后端返回菜品列表
   ↓
4. 前端展示菜品网格
   ↓
5. 用户点击菜品卡片
   ↓
6. 前端调用 API (GET /api/v1/dishes/{id})
   ↓
7. 后端返回完整菜品详情
   ↓
8. 前端在模态框显示详情（食材、步骤）
```

---

## 🔗 API 集成表

| 功能 | API 端点 | 方法 | 前端实现 |
|------|---------|------|--------|
| 健康检查 | `/health` | GET | ✅ 应用启动时调用 |
| 随机菜品 | `/api/v1/dishes/random` | GET | ✅ "随机推荐"按钮 |
| 搜索菜品 | `/api/v1/dishes/search` | GET | ✅ 搜索和过滤功能 |
| 菜品详情 | `/api/v1/dishes/{id}` | GET | ✅ 点击菜品打开详情 |
| 分类列表 | `/api/v1/categories` | GET | ✅ 分类下拉菜单 |
| 系统元数据 | `/api/v1/metadata` | GET | ✅ 应用启动时获取 |
| 食材推荐 | `/api/v1/dishes/recommend` | POST | ✅ "基于食材推荐"功能 |

---

## 📦 依赖说明

| 包名 | 版本 | 用途 |
|------|------|------|
| **vite** | ^6.4.1 | 前端构建工具 |
| **axios** | ^1.13.5 | HTTP 客户端 |
| **tailwindcss** | ^4.1.18 | 样式框架 |
| **postcss** | ^8.5.6 | CSS 处理器 |
| **autoprefixer** | ^10.4.24 | 浏览器前缀 |

---

## 🎨 样式定制

### Tailwind 配置位置
```javascript
// frontend/tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: '#f59e0b',    // 黄色
        secondary: '#8b5cf6',  // 紫色
      }
    }
  }
}
```

### CSS 自定义
编辑 `src/styles.css` 修改：
- 卡片样式 (.card)
- 按钮样式 (.btn-*)
- 标签样式 (.tag)
- 动画效果

---

## 🐛 常见问题

### Q: 打开浏览器后显示"无法连接到后端"
**A:** 确保后端服务已启动
```bash
# 在另一个终端运行
cd /mnt/c/SearchMenu/backend
bash run.sh
```

### Q: Vite 启动失败，提示"端口 5173 已占用"
**A:** 修改端口
```bash
npm run dev -- --port 3000
```

### Q: 页面样式没有加载
**A:** 清除 node_modules 并重新安装
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Q: API 调用失败，但后端正常运行
**A:** 检查 CORS 配置，确保后端已启用 CORS

---

## 🚀 构建和部署

### 开发构建
```bash
npm run build
```

输出目录：`frontend/dist/`

### 预览构建结果
```bash
npm run preview
```

### 部署到服务器
```bash
npm run build
# 将 dist/ 目录上传到服务器
# 配置 Web 服务器（Nginx/Apache）指向 dist/ 目录
```

---

## 📝 代码结构说明

### src/api.js
API 客户端封装，所有 HTTP 请求都通过这个文件
- `dishesAPI.checkHealth()` - 健康检查
- `dishesAPI.getRandomDish()` - 随机菜品
- `dishesAPI.searchDishes()` - 搜索菜品
- `dishesAPI.getCategories()` - 获取分类
- `dishesAPI.getMetadata()` - 获取元数据
- `dishesAPI.getDishDetail()` - 获取菜品详情
- `dishesAPI.recommendDishes()` - 推荐菜品

### src/main.js
应用核心逻辑（600+ 行）
- **状态管理** (state 对象)
- **初始化** (initApp)
- **数据加载** (loadDishes, loadRandomDish, etc.)
- **UI 渲染** (renderDishes, updatePagination, etc.)
- **事件处理** (bindEvents, 按钮点击等)
- **模态框** (showDishModal, showModal等)
- **分页** (prevPage, nextPage等)

### src/styles.css
Tailwind CSS 样式
- 响应式网格
- 卡片组件
- 按钮变体
- 动画效果
- 模态框样式

### index.html
主页面结构（200 行）
- 页面头部
- 搜索和过滤栏
- 食材推荐区域
- 菜品网格
- 分页控制
- 模态框容器

---

## 🎯 前端开发进度

✅ **Day 4 上午：项目初始化**
- ✅ 创建前端目录结构
- ✅ npm init 初始化
- ✅ 安装 Vite、Axios、Tailwind
- ✅ 创建配置文件
- ✅ 创建 HTML 主页面

✅ **Day 4 下午：核心功能实现**
- ✅ 创建 API 客户端 (api.js)
- ✅ 创建应用主逻辑 (main.js)
- ✅ 创建样式文件 (styles.css)
- ✅ 实现搜索、过滤、分页
- ✅ 实现菜品详情和推荐
- ✅ 启动 Vite 开发服务器

⏳ **Day 5：功能完善和测试**
- 测试所有功能
- 优化性能
- 美化界面
- 处理边界情况

---

## ✨ 总结

前端应用已完全实现！

**已完成：**
- ✅ 7 个 API 端点全部集成
- ✅ 所有用户界面功能
- ✅ 响应式设计
- ✅ 错误处理
- ✅ 加载状态

**现在可以：**
1. 启动前端: `bash run.sh`
2. 访问应用: http://localhost:5173
3. 测试所有功能
4. 根据需要调整样式和功能

**后端和前端都已准备好！** 🎉
