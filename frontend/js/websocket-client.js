/**
 * M537 Voice Gateway - WebSocket Client
 * Real-time system status updates
 */
class WebSocketClient {
    constructor(options = {}) {
        this.options = {
            url: this.getWebSocketUrl(),
            reconnectInterval: 3000,
            maxReconnectAttempts: 10,
            onMessage: () => {},
            onConnect: () => {},
            onDisconnect: () => {},
            onError: () => {},
            ...options
        };

        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.shouldReconnect = true;
        this.pingInterval = null;
    }

    getWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${window.location.host}/ws`;
    }

    connect() {
        if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
            return;
        }

        try {
            this.ws = new WebSocket(this.options.url);

            this.ws.onopen = () => {
                console.log('[WebSocket] Connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.options.onConnect();
                this.startPing();
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.options.onMessage(data);
                } catch (e) {
                    console.error('[WebSocket] Failed to parse message:', e);
                }
            };

            this.ws.onclose = (event) => {
                console.log('[WebSocket] Disconnected:', event.code, event.reason);
                this.isConnected = false;
                this.stopPing();
                this.options.onDisconnect();

                if (this.shouldReconnect && this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    this.scheduleReconnect();
                }
            };

            this.ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                this.options.onError(error);
            };

        } catch (e) {
            console.error('[WebSocket] Connection failed:', e);
            this.scheduleReconnect();
        }
    }

    disconnect() {
        this.shouldReconnect = false;
        this.stopPing();
        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }
    }

    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = Math.min(this.options.reconnectInterval * this.reconnectAttempts, 30000);
        console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
    }

    startPing() {
        this.pingInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.send({ type: 'ping' });
            }
        }, 30000);
    }

    stopPing() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    send(data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    refresh() {
        this.send({ type: 'refresh' });
    }
}


/**
 * System Status Monitor
 * Displays real-time system metrics
 */
class SystemStatusMonitor {
    constructor() {
        this.client = null;
        this.statusPanel = null;
        this.lastUpdate = null;
        this.init();
    }

    init() {
        // Create status panel
        this.createStatusPanel();

        // Connect WebSocket
        this.client = new WebSocketClient({
            onMessage: (data) => this.handleMessage(data),
            onConnect: () => this.handleConnect(),
            onDisconnect: () => this.handleDisconnect()
        });

        // Auto-connect after 2 seconds (to not interfere with initial load)
        setTimeout(() => {
            this.client.connect();
        }, 2000);
    }

    createStatusPanel() {
        // Create floating status panel
        const panel = document.createElement('div');
        panel.id = 'systemStatusPanel';
        panel.className = 'system-status-panel';
        panel.innerHTML = `
            <div class="status-header">
                <span class="status-title">系统状态</span>
                <span class="status-indicator disconnected" id="wsIndicator"></span>
            </div>
            <div class="status-body">
                <div class="status-row">
                    <span class="label">CPU</span>
                    <span class="value" id="cpuValue">--</span>
                    <div class="progress-bar"><div class="progress" id="cpuProgress"></div></div>
                </div>
                <div class="status-row">
                    <span class="label">内存</span>
                    <span class="value" id="memValue">--</span>
                    <div class="progress-bar"><div class="progress" id="memProgress"></div></div>
                </div>
                <div class="status-row">
                    <span class="label">磁盘</span>
                    <span class="value" id="diskValue">--</span>
                    <div class="progress-bar"><div class="progress" id="diskProgress"></div></div>
                </div>
                <div class="status-row">
                    <span class="label">容器</span>
                    <span class="value" id="containerValue">--</span>
                </div>
                <div class="status-row">
                    <span class="label">运行</span>
                    <span class="value" id="uptimeValue">--</span>
                </div>
            </div>
            <div class="status-footer">
                <span id="lastUpdateTime">未连接</span>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .system-status-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 200px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                font-size: 12px;
                z-index: 1000;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }

            @media (prefers-color-scheme: dark) {
                .system-status-panel {
                    background: rgba(30, 30, 30, 0.95);
                    color: #fff;
                }
            }

            .status-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 12px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }

            .status-title {
                font-weight: 600;
            }

            .status-indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }

            .status-indicator.connected { background: #10b981; }
            .status-indicator.disconnected { background: #ef4444; }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }

            .status-body {
                padding: 10px 12px;
            }

            .status-row {
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }

            .status-row .label {
                width: 40px;
                color: #666;
            }

            @media (prefers-color-scheme: dark) {
                .status-row .label { color: #999; }
            }

            .status-row .value {
                width: 45px;
                text-align: right;
                font-weight: 500;
                margin-right: 8px;
            }

            .progress-bar {
                flex: 1;
                height: 4px;
                background: rgba(0, 0, 0, 0.1);
                border-radius: 2px;
                overflow: hidden;
            }

            .progress {
                height: 100%;
                background: #2563eb;
                border-radius: 2px;
                transition: width 0.5s ease;
            }

            .progress.warning { background: #f59e0b; }
            .progress.danger { background: #ef4444; }

            .status-footer {
                padding: 8px 12px;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
                text-align: center;
                color: #999;
                font-size: 10px;
            }

            @media (max-width: 768px) {
                .system-status-panel {
                    top: auto;
                    bottom: 20px;
                    right: 10px;
                    left: 10px;
                    width: auto;
                }
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(panel);
        this.statusPanel = panel;
    }

    handleConnect() {
        const indicator = document.getElementById('wsIndicator');
        if (indicator) {
            indicator.className = 'status-indicator connected';
        }
    }

    handleDisconnect() {
        const indicator = document.getElementById('wsIndicator');
        if (indicator) {
            indicator.className = 'status-indicator disconnected';
        }
        document.getElementById('lastUpdateTime').textContent = '连接断开';
    }

    handleMessage(data) {
        if (data.type === 'system_status') {
            this.updateDisplay(data.data);
            this.lastUpdate = new Date();
            document.getElementById('lastUpdateTime').textContent =
                '更新于 ' + this.lastUpdate.toLocaleTimeString();
        } else if (data.type === 'pong') {
            // Heartbeat response
        }
    }

    updateDisplay(data) {
        // Update CPU
        const cpu = data.system?.cpu || 0;
        document.getElementById('cpuValue').textContent = cpu.toFixed(1) + '%';
        const cpuProgress = document.getElementById('cpuProgress');
        cpuProgress.style.width = cpu + '%';
        cpuProgress.className = 'progress' + (cpu > 90 ? ' danger' : cpu > 70 ? ' warning' : '');

        // Update Memory
        const mem = data.system?.memory || 0;
        document.getElementById('memValue').textContent = mem.toFixed(1) + '%';
        const memProgress = document.getElementById('memProgress');
        memProgress.style.width = mem + '%';
        memProgress.className = 'progress' + (mem > 90 ? ' danger' : mem > 70 ? ' warning' : '');

        // Update Disk
        const disk = data.system?.disk || 0;
        document.getElementById('diskValue').textContent = disk.toFixed(1) + '%';
        const diskProgress = document.getElementById('diskProgress');
        diskProgress.style.width = disk + '%';
        diskProgress.className = 'progress' + (disk > 90 ? ' danger' : disk > 80 ? ' warning' : '');

        // Update Containers
        const containers = data.containers || {};
        document.getElementById('containerValue').textContent =
            `${containers.running || 0} / ${containers.total || 0}`;

        // Update Uptime
        document.getElementById('uptimeValue').textContent = data.uptime || '--';
    }
}

// Auto-initialize on load
document.addEventListener('DOMContentLoaded', () => {
    // Only init on desktop (to save mobile bandwidth)
    if (window.innerWidth > 768) {
        window.systemMonitor = new SystemStatusMonitor();
    }
});
