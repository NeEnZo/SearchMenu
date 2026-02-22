# 🍽️ SearchMenu

基于 [HowToCook](https://github.com/Anduin2017/HowToCook) 菜谱数据的搜索与推荐平台。支持随机推荐、按食材推荐、分类/难度筛选及菜品详情查看。

**🔗 在线体验：[search-menu-lime.vercel.app](https://search-menu-lime.vercel.app)**

> 后端托管于 Render 免费计划，15 分钟无请求后休眠，首次访问约需 30 秒冷启动。

## 技术栈

| 层次 | 技术 | 部署 |
|------|------|------|
| 后端 | Python 3.11 · FastAPI · SQLite | Render |
| 前端 | Vanilla JS · Vite · Tailwind CSS | Vercel |
| 数据 | HowToCook（342 道菜谱） | 打包进镜像 |

## 本地开发

```bash
# 后端（首次需初始化数据库）
cd backend
pip install -r requirements.txt
python scripts/init_db.py        # 仅首次
uvicorn app.main:app --reload --port 8000
# API 文档：http://localhost:8000/docs

# 前端（新终端）
cd frontend
npm install
npm run dev
# 终端会显示实际监听端口
```

## 数据来源

菜谱数据来自 [HowToCook](https://github.com/Anduin2017/HowToCook)，MIT 协议开源。
