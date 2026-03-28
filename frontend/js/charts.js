/**
 * M537 Voice Gateway - Data Visualization
 * Real-time charts for system metrics
 */

class MetricsCharts {
    constructor() {
        this.charts = {};
        this.history = {
            cpu: [],
            memory: [],
            disk: [],
            timestamps: []
        };
        this.maxDataPoints = 60; // 5 minutes at 5-second intervals
        this.chartContainer = null;
        this.isVisible = false;
    }

    init() {
        this.createChartPanel();
        this.setupToggleButton();
    }

    createChartPanel() {
        const panel = document.createElement('div');
        panel.id = 'metricsChartPanel';
        panel.className = 'metrics-chart-panel hidden';
        panel.innerHTML = `
            <div class="chart-header">
                <h3>System Metrics</h3>
                <button class="chart-close-btn">&times;</button>
            </div>
            <div class="chart-body">
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="diskChart"></canvas>
                </div>
            </div>
            <div class="chart-footer">
                <span class="chart-time-range">Last 5 minutes</span>
                <button class="chart-refresh-btn">Refresh</button>
            </div>
        `;

        // Add styles
        this.addStyles();

        document.body.appendChild(panel);
        this.chartContainer = panel;

        // Event handlers
        panel.querySelector('.chart-close-btn').addEventListener('click', () => this.hide());
        panel.querySelector('.chart-refresh-btn').addEventListener('click', () => this.refresh());

        // Initialize charts
        this.initCharts();
    }

    addStyles() {
        if (document.getElementById('chart-styles')) return;

        const style = document.createElement('style');
        style.id = 'chart-styles';
        style.textContent = `
            .metrics-chart-panel {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 90%;
                max-width: 800px;
                max-height: 80vh;
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                z-index: 10001;
                overflow: hidden;
                animation: chartSlideIn 0.3s ease;
            }

            @keyframes chartSlideIn {
                from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
                to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }

            .metrics-chart-panel.hidden {
                display: none;
            }

            @media (prefers-color-scheme: dark) {
                .metrics-chart-panel {
                    background: #1e1e1e;
                    color: #fff;
                }
            }

            .chart-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                border-bottom: 1px solid #eee;
            }

            @media (prefers-color-scheme: dark) {
                .chart-header { border-color: #333; }
            }

            .chart-header h3 {
                margin: 0;
                font-size: 18px;
            }

            .chart-close-btn {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
                padding: 0;
                line-height: 1;
            }

            .chart-body {
                padding: 20px;
                max-height: 60vh;
                overflow-y: auto;
                display: grid;
                gap: 20px;
            }

            .chart-container {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 16px;
                height: 150px;
            }

            @media (prefers-color-scheme: dark) {
                .chart-container { background: #2d2d2d; }
            }

            .chart-container canvas {
                width: 100% !important;
                height: 100% !important;
            }

            .chart-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 20px;
                border-top: 1px solid #eee;
            }

            @media (prefers-color-scheme: dark) {
                .chart-footer { border-color: #333; }
            }

            .chart-time-range {
                font-size: 12px;
                color: #666;
            }

            .chart-refresh-btn {
                background: #4a90d9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }

            .chart-refresh-btn:hover {
                background: #357abd;
            }

            .chart-toggle-btn {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: #4a90d9;
                color: white;
                border: none;
                width: 48px;
                height: 48px;
                border-radius: 50%;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(74, 144, 217, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                transition: transform 0.2s;
            }

            .chart-toggle-btn:hover {
                transform: scale(1.1);
            }

            .chart-toggle-btn svg {
                width: 24px;
                height: 24px;
            }

            .chart-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 10000;
            }

            .chart-overlay.hidden {
                display: none;
            }
        `;
        document.head.appendChild(style);
    }

    setupToggleButton() {
        const btn = document.createElement('button');
        btn.className = 'chart-toggle-btn';
        btn.title = 'Show Charts';
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 20V10M12 20V4M6 20v-6"/>
            </svg>
        `;
        btn.addEventListener('click', () => this.toggle());
        document.body.appendChild(btn);

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'chart-overlay hidden';
        overlay.addEventListener('click', () => this.hide());
        document.body.appendChild(overlay);
        this.overlay = overlay;
    }

    initCharts() {
        // Simple canvas-based charts (no external dependencies)
        this.charts.cpu = new SimpleLineChart('cpuChart', {
            label: 'CPU Usage (%)',
            color: '#4a90d9',
            max: 100
        });

        this.charts.memory = new SimpleLineChart('memoryChart', {
            label: 'Memory Usage (%)',
            color: '#10b981',
            max: 100
        });

        this.charts.disk = new SimpleLineChart('diskChart', {
            label: 'Disk Usage (%)',
            color: '#f59e0b',
            max: 100
        });
    }

    show() {
        this.chartContainer.classList.remove('hidden');
        this.overlay.classList.remove('hidden');
        this.isVisible = true;
        this.refresh();
    }

    hide() {
        this.chartContainer.classList.add('hidden');
        this.overlay.classList.add('hidden');
        this.isVisible = false;
    }

    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }

    addDataPoint(cpu, memory, disk) {
        const now = new Date();
        this.history.timestamps.push(now);
        this.history.cpu.push(cpu);
        this.history.memory.push(memory);
        this.history.disk.push(disk);

        // Keep only last N data points
        if (this.history.timestamps.length > this.maxDataPoints) {
            this.history.timestamps.shift();
            this.history.cpu.shift();
            this.history.memory.shift();
            this.history.disk.shift();
        }

        // Update charts if visible
        if (this.isVisible) {
            this.updateCharts();
        }
    }

    updateCharts() {
        this.charts.cpu.update(this.history.cpu);
        this.charts.memory.update(this.history.memory);
        this.charts.disk.update(this.history.disk);
    }

    refresh() {
        // Fetch current metrics
        fetch('/api/metrics/json')
            .then(r => r.json())
            .then(data => {
                console.log('[Charts] Metrics refreshed');
            })
            .catch(err => {
                console.error('[Charts] Failed to fetch metrics:', err);
            });
    }
}

/**
 * Simple canvas-based line chart (no dependencies)
 */
class SimpleLineChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = {
            label: options.label || 'Value',
            color: options.color || '#4a90d9',
            max: options.max || 100,
            padding: 40
        };
        this.data = [];

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.draw();
    }

    update(data) {
        this.data = data;
        this.draw();
    }

    draw() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const p = this.options.padding;

        // Clear
        ctx.clearRect(0, 0, w, h);

        // Check dark mode
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const textColor = isDark ? '#fff' : '#333';
        const gridColor = isDark ? '#444' : '#ddd';

        // Draw grid
        ctx.strokeStyle = gridColor;
        ctx.lineWidth = 1;

        // Horizontal lines
        for (let i = 0; i <= 4; i++) {
            const y = p + (h - 2 * p) * (i / 4);
            ctx.beginPath();
            ctx.moveTo(p, y);
            ctx.lineTo(w - p, y);
            ctx.stroke();

            // Labels
            ctx.fillStyle = textColor;
            ctx.font = '10px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText(`${Math.round(this.options.max * (1 - i / 4))}%`, p - 5, y + 3);
        }

        // Draw label
        ctx.fillStyle = textColor;
        ctx.font = 'bold 12px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(this.options.label, p, 15);

        // Draw current value
        if (this.data.length > 0) {
            const current = this.data[this.data.length - 1];
            ctx.textAlign = 'right';
            ctx.fillText(`${current.toFixed(1)}%`, w - p, 15);
        }

        // Draw line
        if (this.data.length < 2) return;

        const chartW = w - 2 * p;
        const chartH = h - 2 * p;

        ctx.beginPath();
        ctx.strokeStyle = this.options.color;
        ctx.lineWidth = 2;
        ctx.lineJoin = 'round';

        this.data.forEach((val, i) => {
            const x = p + (i / (this.data.length - 1)) * chartW;
            const y = p + chartH - (val / this.options.max) * chartH;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();

        // Draw fill
        ctx.lineTo(p + chartW, p + chartH);
        ctx.lineTo(p, p + chartH);
        ctx.closePath();
        ctx.fillStyle = this.options.color + '20';
        ctx.fill();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.metricsCharts = new MetricsCharts();
    window.metricsCharts.init();
});

// Integration with WebSocket status monitor
if (window.systemMonitor) {
    const originalHandleMessage = window.systemMonitor.handleMessage;
    window.systemMonitor.handleMessage = function(data) {
        originalHandleMessage.call(this, data);

        if (data.type === 'system_status' && window.metricsCharts) {
            const sys = data.data?.system || {};
            window.metricsCharts.addDataPoint(
                sys.cpu || 0,
                sys.memory || 0,
                sys.disk || 0
            );
        }
    };
}
