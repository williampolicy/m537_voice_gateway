# M537 Voice Gateway - 故障排查指南

> 版本: 1.0.0 | 标准: LIGHT HOPE V5.3

## 快速诊断

```bash
# 一键诊断脚本
bash scripts/health_check.sh
```

---

## 常见问题

### 1. 容器无法启动

**症状**: `docker compose up` 失败

**检查步骤**:

```bash
# 1. 查看详细错误
docker compose logs

# 2. 检查端口占用
lsof -i:5537
netstat -tlnp | grep 5537

# 3. 检查 Docker 资源
docker system df
docker system prune -f  # 清理未使用资源
```

**解决方案**:

```bash
# 端口被占用
kill $(lsof -t -i:5537)
docker compose up -d

# 镜像损坏
docker compose build --no-cache
docker compose up -d
```

---

### 2. 健康检查失败

**症状**: 容器反复重启，健康状态 unhealthy

**检查步骤**:

```bash
# 1. 查看容器状态
docker ps -a --filter name=m537

# 2. 查看健康检查日志
docker inspect m537_voice_gateway | grep -A 10 Health

# 3. 手动测试健康端点
docker exec m537_voice_gateway curl -f http://localhost:5537/health
```

**解决方案**:

```bash
# 服务启动慢，增加 start_period
# 编辑 docker-compose.yml:
healthcheck:
  start_period: 60s  # 增加启动等待时间

# 重新部署
docker compose up -d
```

---

### 3. 语音识别不工作

**症状**: 点击录音按钮无反应

**检查步骤**:

1. 检查浏览器控制台错误 (F12)
2. 确认使用 HTTPS 或 localhost
3. 检查麦克风权限

**解决方案**:

- 使用 Chrome 或 Edge 浏览器
- 允许麦克风权限
- 使用 HTTPS 访问 (非 localhost)

```javascript
// 检查浏览器支持
const supported = 'webkitSpeechRecognition' in window
               || 'SpeechRecognition' in window;
console.log('语音识别支持:', supported);
```

---

### 4. 查询返回空结果

**症状**: API 返回成功但数据为空

**检查步骤**:

```bash
# 1. 检查项目目录挂载
docker exec m537_voice_gateway ls /data/projects

# 2. 检查权限
docker exec m537_voice_gateway ls -la /data/projects | head

# 3. 测试特定工具
docker exec m537_voice_gateway python -c "
from tools.count_projects import CountProjectsTool
tool = CountProjectsTool()
print(tool.execute({}))
"
```

**解决方案**:

```yaml
# 确保 docker-compose.yml 中挂载正确
volumes:
  - /data/projects:/data/projects:ro
```

---

### 5. 内存超限

**症状**: 容器被 OOM Killer 杀死

**检查步骤**:

```bash
# 查看内存使用
docker stats m537_voice_gateway

# 查看 OOM 事件
dmesg | grep -i "out of memory"
```

**解决方案**:

```bash
# 1. 重启容器
docker compose restart

# 2. 如果持续超限，检查是否有内存泄漏
docker compose logs | grep -i "memory\|error"
```

---

### 6. 意图识别错误

**症状**: 系统无法理解用户问题

**检查步骤**:

```bash
# 测试意图解析
curl -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"你的问题"}' | jq '.data.intent'
```

**解决方案**:

1. 检查 `backend/config/intent_rules.py` 中的关键词
2. 添加更多关键词变体
3. 使用更精确的表达方式

---

### 7. TTS 语音播报无声音

**症状**: 查询成功但无语音播报

**检查步骤**:

1. 检查系统音量
2. 检查浏览器控制台错误
3. 测试浏览器 TTS

```javascript
// 在浏览器控制台测试
const utterance = new SpeechSynthesisUtterance('测试语音');
utterance.lang = 'zh-CN';
speechSynthesis.speak(utterance);
```

**解决方案**:

- 确保浏览器支持 Web Speech API
- 检查是否有中文语音包
- 尝试更换浏览器

---

### 8. Docker 网络问题

**症状**: 容器间无法通信

**检查步骤**:

```bash
# 检查网络
docker network ls
docker network inspect lighthope_network
```

**解决方案**:

当前配置使用 `network_mode: host`，无需额外网络配置。

如果使用桥接网络：
```bash
docker network create lighthope_network
docker compose up -d
```

---

## 日志分析

### 查看应用日志

```bash
# 实时日志
docker compose logs -f

# 最近 100 行
docker compose logs --tail=100

# 过滤错误
docker compose logs | grep -i "error\|exception"
```

### 日志位置

- 容器日志: `docker compose logs`
- 应用日志: `/data/projects/m537_voice_gateway/logs/`

---

## 性能问题

### 响应慢

```bash
# 检查响应时间
curl -w "Time: %{time_total}s\n" -X POST \
  http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"有多少项目"}'
```

### CPU 使用高

```bash
# 查看 CPU 使用
docker stats m537_voice_gateway

# 查看进程
docker exec m537_voice_gateway top -b -n 1
```

---

## 紧急恢复

### 完全重置

```bash
# 停止并删除所有相关资源
docker compose down -v
docker rmi m537_voice_gateway

# 重新构建和启动
docker compose build --no-cache
docker compose up -d
```

---

## 联系支持

如果以上方案无法解决问题：

1. 收集诊断信息: `bash scripts/health_check.sh > diagnosis.txt`
2. 导出日志: `docker compose logs > logs.txt`
3. 提交 Issue 或联系维护团队

---

*LIGHT HOPE V5.3 Compliant*
