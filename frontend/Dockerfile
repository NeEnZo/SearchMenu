# ---- 构建阶段 ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# 注入 API URL（docker-compose 或 Vercel 构建时通过 build arg 传入）
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ---- 运行阶段：Nginx 静态服务 ----
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# SPA 路由支持：所有路径回退到 index.html
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
