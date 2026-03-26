#!/bin/bash
# M537 Voice Gateway - API Integration Test
# Tests all API endpoints against running service

BASE_URL="${1:-http://localhost:5537}"
PASS=0
FAIL=0

echo "=============================================="
echo "M537 API Integration Test"
echo "Base URL: $BASE_URL"
echo "=============================================="
echo ""

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local expected_content="$6"

    # Delay to avoid rate limiting (60 req/min = 1 req/sec)
    sleep 0.5

    echo -n "Testing: $name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi

    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status" = "$expected_status" ]; then
        if [ -n "$expected_content" ]; then
            if echo "$body" | grep -q "$expected_content"; then
                echo "PASS"
                ((PASS++))
            else
                echo "FAIL (missing content: $expected_content)"
                ((FAIL++))
            fi
        else
            echo "PASS"
            ((PASS++))
        fi
    else
        echo "FAIL (status: $status, expected: $expected_status)"
        ((FAIL++))
    fi
}

echo "--- Health & Info Endpoints ---"
test_endpoint "Health Check" "GET" "/health" "" "200" "healthy"
test_endpoint "API Health" "GET" "/api/health" "" "200" "healthy"
test_endpoint "Version" "GET" "/api/version" "" "200" "m537"
test_endpoint "Metrics (Prometheus)" "GET" "/api/metrics" "" "200" "m537_requests_total"
test_endpoint "Metrics (JSON)" "GET" "/api/metrics/json" "" "200" "requests"
test_endpoint "Uptime Check" "GET" "/api/uptime" "" "200" "OK"
test_endpoint "Uptime Simple" "GET" "/api/uptime/simple" "" "200" "OK"

echo ""
echo "--- Voice Query Endpoints ---"
test_endpoint "Count Projects" "POST" "/api/voice-query" '{"transcript":"有多少个项目"}' "200" "success"
test_endpoint "System Status" "POST" "/api/voice-query" '{"transcript":"系统状态怎么样"}' "200" "success"
test_endpoint "List Ports" "POST" "/api/voice-query" '{"transcript":"当前有哪些端口在监听"}' "200" "success"
test_endpoint "Recent Errors" "POST" "/api/voice-query" '{"transcript":"最近有什么错误"}' "200" "success"
test_endpoint "Docker Containers" "POST" "/api/voice-query" '{"transcript":"哪些Docker容器在运行"}' "200" "success"
test_endpoint "P0 Health" "POST" "/api/voice-query" '{"transcript":"P0服务状态如何"}' "200" "success"
test_endpoint "Project Summary" "POST" "/api/voice-query" '{"transcript":"m537是什么项目"}' "200" "success"
test_endpoint "Missing README" "POST" "/api/voice-query" '{"transcript":"哪些项目没有README"}' "200" "success"
test_endpoint "Recent Updates" "POST" "/api/voice-query" '{"transcript":"最近更新了什么"}' "200" "success"
test_endpoint "Tmux Sessions" "POST" "/api/voice-query" '{"transcript":"当前有哪些tmux会话"}' "200" "success"

echo ""
echo "--- Error Handling ---"
test_endpoint "Unknown Intent" "POST" "/api/voice-query" '{"transcript":"今天天气怎么样"}' "200" "INTENT_NOT_RECOGNIZED"
test_endpoint "Empty Transcript" "POST" "/api/voice-query" '{"transcript":""}' "422" ""
test_endpoint "With Session ID" "POST" "/api/voice-query" '{"transcript":"系统状态","session_id":"test-session-123"}' "200" "success"

echo ""
echo "--- Frontend ---"
test_endpoint "Index Page" "GET" "/" "" "200" "M537"
test_endpoint "CSS Styles" "GET" "/css/styles.css" "" "200" "M537"
test_endpoint "JS App" "GET" "/js/app.js" "" "200" "App"

echo ""
echo "=============================================="
echo "Results: $PASS passed, $FAIL failed"
echo "=============================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
exit 0
