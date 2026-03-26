#!/bin/bash
# M537 Voice Gateway Health Check Script

echo "=== M537 Health Check ==="
echo "Date: $(date)"
echo ""

# 1. Container status
echo -n "1. Container running... "
if docker ps | grep m537_voice_gateway > /dev/null 2>&1; then
    echo "OK"
else
    echo "FAILED"
fi

# 2. Health endpoint
echo -n "2. Health endpoint... "
if curl -sf http://localhost:5537/health > /dev/null 2>&1; then
    echo "OK"
else
    echo "FAILED"
fi

# 3. Memory usage
echo -n "3. Memory usage... "
MEM=$(docker stats --no-stream m537_voice_gateway --format "{{.MemUsage}}" 2>/dev/null | cut -d'/' -f1)
if [ -n "$MEM" ]; then
    echo "OK ($MEM)"
else
    echo "UNKNOWN"
fi

# 4. Restart policy
echo -n "4. Restart policy... "
POLICY=$(docker inspect m537_voice_gateway --format '{{.HostConfig.RestartPolicy.Name}}' 2>/dev/null)
if [ "$POLICY" = "unless-stopped" ]; then
    echo "OK ($POLICY)"
else
    echo "WARNING ($POLICY)"
fi

# 5. API test
echo -n "5. API response... "
RESPONSE=$(curl -sf -X POST http://localhost:5537/api/voice-query \
  -H "Content-Type: application/json" \
  -d '{"transcript":"测试"}' 2>/dev/null)
if [ -n "$RESPONSE" ]; then
    echo "OK"
else
    echo "FAILED"
fi

echo ""
echo "=== Check Complete ==="
