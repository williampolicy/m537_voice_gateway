# M537 Voice Gateway - 部署指南

> 版本: 1.0.0 | 标准: LIGHT HOPE V5.3

## 前置条件

### 系统要求

- Docker 24.0+
- Docker Compose 2.24+
- 1GB 可用内存
- 端口 5537 可用

### 环境要求

```bash
# 检查 Docker 版本
docker --version
docker compose version

# 检查端口可用性
lsof -i:5537
```

---

## 快速部署

### 一键部署

```bash
cd /data/projects/m537_voice_gateway
docker compose up -d --build
```

### 验证部署

```bash
# 健康检查
curl http://localhost:5537/health

# 测试查询
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"现在有多少个项目"}'
```

---

## 详细部署步骤

### 1. 克隆/进入项目目录

```bash
cd /data/projects/m537_voice_gateway
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置 (可选)
nano .env
```

### 3. 构建镜像

```bash
docker compose build
```

### 4. 启动服务

```bash
docker compose up -d
```

### 5. 查看日志

```bash
docker compose logs -f
```

---

## Cloudflare Tunnel 配置

### 1. 添加隧道路由

编辑 Cloudflare Tunnel 配置文件：

```yaml
# /etc/cloudflared/config.yml
ingress:
  - hostname: voice.x1000.ai
    service: http://localhost:5537
  - service: http_status:404
```

### 2. 重启 Tunnel

```bash
sudo systemctl restart cloudflared
```

### 3. 验证外部访问

```bash
curl https://voice.x1000.ai/health
```

---

## V5.3 合规检查

| 检查项 | 要求 | 验证命令 |
|--------|------|----------|
| 内存限制 | ≤ 1G | `docker stats m537_voice_gateway` |
| 自动重启 | unless-stopped | `docker inspect m537_voice_gateway \| grep RestartPolicy` |
| 健康检查 | /health 端点 | `curl localhost:5537/health` |
| 日志限制 | max-size 10m | 检查 docker-compose.yml |
| README | > 100 行 | `wc -l README.md` |

---

## 运维操作

### 查看状态

```bash
docker ps --filter name=m537
docker stats m537_voice_gateway
```

### 查看日志

```bash
docker compose logs -f --tail=100
```

### 重启服务

```bash
docker compose restart
```

### 停止服务

```bash
docker compose down
```

### 更新部署

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 回滚

```bash
# 停止当前版本
docker compose down

# 恢复到之前的镜像 (如果有)
docker compose up -d
```

---

## 故障排查

### 容器无法启动

```bash
# 检查日志
docker compose logs

# 检查端口占用
lsof -i:5537

# 检查资源
docker system df
```

### 健康检查失败

```bash
# 进入容器
docker exec -it m537_voice_gateway bash

# 手动测试
curl localhost:5537/health
```

### 内存超限

```bash
# 检查内存使用
docker stats m537_voice_gateway

# 重启服务
docker compose restart
```

---

## 监控

### Prometheus 指标

```bash
curl http://localhost:5537/api/metrics
```

### Uptime Kuma 监控

M537 Voice Gateway 支持 Uptime Kuma 监控。

#### HTTP 监控 (推荐)

在 Uptime Kuma 中添加 HTTP(s) 监控：

| 设置 | 值 |
|------|---|
| 监控类型 | HTTP(s) |
| URL | `https://voice.x1000.ai/api/uptime` |
| 监控间隔 | 60 秒 |
| 重试次数 | 3 |
| 关键字 | `OK` |

#### Push 监控 (可选)

1. 在 Uptime Kuma 创建 Push 监控，获取 Push URL
2. 设置环境变量：

```bash
export UPTIME_KUMA_PUSH_URL="https://your-kuma.com/api/push/xxxxx"
```

3. 服务会自动每 60 秒推送心跳

#### 简单监控端点

```bash
# JSON 响应
curl https://voice.x1000.ai/api/uptime

# 纯文本响应 (最小开销)
curl https://voice.x1000.ai/api/uptime/simple
```

### 日志位置

- 容器日志: `docker compose logs`
- 应用日志: `./logs/` 目录

---

*LIGHT HOPE V5.3 Compliant*
