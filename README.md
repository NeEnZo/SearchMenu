# 🍽️ SearchMenu

基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 的菜品搜索与推荐平台。支持随机推荐、按食材推荐、分类/难度筛选及菜品详情查看。

**🔗 在线体验：[search-menu-lime.vercel.app](https://search-menu-lime.vercel.app)**　　**📖 API 文档：[searchmenu-backend.onrender.com/docs](https://searchmenu-backend.onrender.com/docs)**

> ⚠️ 后端部署在 Render 免费计划，15 分钟无请求后休眠，首次访问约需 30 秒冷启动。

## 技术栈

| 层次 | 技术 | 部署平台 |
|------|------|------|
| 后端 | Python 3.11 + FastAPI + SQLite | Render |
| 前端 | Vanilla JS + Vite + Tailwind CSS | Vercel |
| 数据 | HowToCook（342 道菜谱） | 打包进镜像 |

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

> 顺序：**先部署后端取得域名，再部署前端注入域名，最后回后端配置 CORS**。

### 第一步：后端部署到 Render

1. 将项目推送到 GitHub（根目录已有 `render.yaml`）
2. 登录 [Render](https://render.com) → **New → Blueprint** → 关联仓库，Render 自动读取 `render.yaml`
3. 部署完成后记录地址，例如 `https://searchmenu-backend.onrender.com`
4. 验证：访问 `/health` 返回 `{"status":"ok"}` 即成功

### 第二步：前端部署到 Vercel

1. 登录 [Vercel](https://vercel.com) → **Add New → Project** → 选择同一仓库
2. **Root Directory** 设为 `frontend/`，Framework 自动识别 Vite
3. **Settings → Environment Variables** 添加：
   ```
   VITE_API_BASE_URL = https://searchmenu-backend.onrender.com
   ```
4. 点击 **Redeploy**（确保环境变量打入构建产物）

### 第三步：回 Render 配置跨域白名单

前端部署完成后得到 Vercel 域名，在 Render 后端服务的环境变量中添加：
```
ALLOWED_ORIGINS = https://search-menu-lime.vercel.app
```
Render 自动重新部署，CORS 配置生效。

## 数据来源

所有菜谱数据来自 [HowToCook](https://github.com/Anduin2017/HowToCook)，该项目以 MIT 协议开源。
