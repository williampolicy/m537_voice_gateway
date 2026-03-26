#!/bin/bash
# M537 Voice Gateway - Cloudflare Tunnel 配置脚本
# LIGHT HOPE V5.3 Compliant

set -e

DOMAIN="voice.x1000.ai"
LOCAL_PORT="5537"
CONFIG_FILE="/etc/cloudflared/config.yml"

echo "=== M537 Cloudflare Tunnel 配置 ==="

# 检查 cloudflared 是否安装
if ! command -v cloudflared &> /dev/null; then
    echo "错误: cloudflared 未安装"
    echo "请先安装: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation"
    exit 1
fi

# 检查服务是否运行
echo "检查 M537 服务..."
if ! curl -sf http://localhost:${LOCAL_PORT}/health > /dev/null; then
    echo "错误: M537 服务未运行在端口 ${LOCAL_PORT}"
    echo "请先启动服务: docker compose up -d"
    exit 1
fi
echo "✅ M537 服务运行正常"

# 显示当前配置
echo ""
echo "当前 Cloudflare Tunnel 配置:"
if [ -f "$CONFIG_FILE" ]; then
    cat "$CONFIG_FILE"
else
    echo "配置文件不存在: $CONFIG_FILE"
fi

echo ""
echo "=== 配置说明 ==="
echo ""
echo "请在 $CONFIG_FILE 中添加以下配置:"
echo ""
cat << 'EOF'
ingress:
  # ... 其他服务 ...

  - hostname: voice.x1000.ai
    service: http://localhost:5537

  - service: http_status:404
EOF

echo ""
echo "然后重启 cloudflared:"
echo "  sudo systemctl restart cloudflared"
echo ""
echo "或者使用命令行添加路由:"
echo "  cloudflared tunnel route dns <TUNNEL_ID> ${DOMAIN}"
echo ""

# 可选：自动添加配置
read -p "是否尝试自动添加配置? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$CONFIG_FILE" ]; then
        # 检查是否已存在配置
        if grep -q "voice.x1000.ai" "$CONFIG_FILE"; then
            echo "配置已存在，跳过..."
        else
            echo "需要 root 权限来修改配置文件..."
            echo "请手动添加配置或使用 sudo 运行此脚本"
        fi
    else
        echo "配置文件不存在，请手动创建"
    fi
fi

echo ""
echo "=== 验证步骤 ==="
echo "1. 确保 Cloudflare Tunnel 配置正确"
echo "2. 重启 cloudflared 服务"
echo "3. 测试访问: curl https://${DOMAIN}/health"
echo ""
echo "完成！"
