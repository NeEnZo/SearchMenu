# 构建上下文必须设为项目根目录（见根目录 docker-compose.yml 或 Render 设置）
# ---- 构建阶段：生成 SQLite 数据库 ----
FROM python:3.11-slim AS builder

WORKDIR /build

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY backend/scripts/ ./scripts/
COPY how-to-cook-data/ ./how-to-cook-data/

RUN python scripts/init_db.py

# ---- 运行阶段 ----
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY --from=builder /build/search_menu.db ./search_menu.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
