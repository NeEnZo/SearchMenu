# 🍽️ SearchMenu

基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 的菜品搜索与推荐平台。支持随机推荐、按食材推荐、分类/难度筛选及菜品详情查看。

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLite |
| 前端 | Vanilla JS + Vite + Tailwind CSS |
| 数据 | HowToCook（342 道菜谱） |

## 本地开发

### 1. 启动后端

```bash
cd backend
# 首次运行：初始化数据库
python scripts/init_db.py
# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

后端运行于 http://localhost:8000，API 文档见 http://localhost:8000/docs

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行于 http://localhost:5173

### 3. Docker 一键启动（推荐）

```bash
docker-compose up --build
```

访问 http://localhost:5173

## 部署

### 后端部署到 Render

1. 将项目推送到 GitHub
2. 在 [Render](https://render.com) 创建 **Web Service**，选择 Docker 方式
3. 根目录设为 `backend/`，或直接使用根目录的 `docker-compose.yml`
4. 环境变量无需额外配置（SQLite 数据打包在镜像中）

### 前端部署到 Vercel

1. 在 [Vercel](https://vercel.com) 导入 GitHub 仓库
2. 框架预设选 **Vite**，根目录设为 `frontend/`
3. 添加环境变量 `VITE_API_BASE_URL=https://你的后端域名`
4. 部署完成

## 数据来源

所有菜谱数据来自 [HowToCook](https://github.com/Anduin2017/HowToCook)，该项目以 MIT 协议开源。
