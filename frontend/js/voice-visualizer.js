/**
 * M537 Voice Visualizer Module
 * Real-time audio waveform visualization using Web Audio API
 */
class VoiceVisualizer {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas element not found:', canvasId);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationId = null;
        this.isActive = false;
        this.stream = null;

        // Options
        this.barCount = options.barCount || 32;
        this.barColor = options.barColor || '#2563eb';
        this.barColorActive = options.barColorActive || '#ef4444';
        this.backgroundColor = options.backgroundColor || 'transparent';
        this.minBarHeight = options.minBarHeight || 2;
        this.barSpacing = options.barSpacing || 2;
        this.smoothing = options.smoothing || 0.8;

        this.setupCanvas();
        this.drawIdleState();
    }

    setupCanvas() {
        // Handle high DPI displays
        const rect = this.canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;

        this.ctx.scale(dpr, dpr);

        // Store display dimensions
        this.displayWidth = rect.width;
        this.displayHeight = rect.height;
    }

    async start() {
        if (this.isActive) return;

        try {
            // Get microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            // Create analyser
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 128;
            this.analyser.smoothingTimeConstant = this.smoothing;

            // Connect microphone to analyser
            const source = this.audioContext.createMediaStreamSource(this.stream);
            source.connect(this.analyser);

            // Create data array
            this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);

            this.isActive = true;
            this.animate();

            if (CONFIG?.DEBUG) console.log('Visualizer started');
        } catch (error) {
            console.error('Failed to start visualizer:', error);
        }
    }

    stop() {
        this.isActive = false;

        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }

        // Draw idle state after stopping
        setTimeout(() => this.drawIdleState(), 100);

        if (CONFIG?.DEBUG) console.log('Visualizer stopped');
    }

    animate() {
        if (!this.isActive) return;

        this.analyser.getByteFrequencyData(this.dataArray);
        this.draw(this.dataArray);

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    draw(dataArray) {
        const { ctx, displayWidth, displayHeight, barCount, minBarHeight, barSpacing } = this;

        // Clear canvas
        ctx.clearRect(0, 0, displayWidth, displayHeight);

        // Calculate bar dimensions
        const totalSpacing = (barCount - 1) * barSpacing;
        const barWidth = (displayWidth - totalSpacing) / barCount;
        const maxBarHeight = displayHeight * 0.9;
        const centerY = displayHeight / 2;

        // Draw bars
        for (let i = 0; i < barCount; i++) {
            // Map frequency data to bar index
            const dataIndex = Math.floor(i * (dataArray.length / barCount));
            const value = dataArray[dataIndex] || 0;

            // Calculate bar height (symmetric around center)
            const normalizedValue = value / 255;
            const barHeight = Math.max(minBarHeight, normalizedValue * maxBarHeight);

            // Calculate position
            const x = i * (barWidth + barSpacing);
            const y = centerY - barHeight / 2;

            // Create gradient for active bars
            const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
            gradient.addColorStop(0, this.barColorActive);
            gradient.addColorStop(0.5, this.barColor);
            gradient.addColorStop(1, this.barColorActive);

            // Draw bar with rounded corners
            ctx.fillStyle = gradient;
            this.roundRect(ctx, x, y, barWidth, barHeight, barWidth / 2);
            ctx.fill();
        }
    }

    drawIdleState() {
        const { ctx, displayWidth, displayHeight, barCount, minBarHeight, barSpacing } = this;

        ctx.clearRect(0, 0, displayWidth, displayHeight);

        const totalSpacing = (barCount - 1) * barSpacing;
        const barWidth = (displayWidth - totalSpacing) / barCount;
        const centerY = displayHeight / 2;

        // Draw subtle idle bars
        for (let i = 0; i < barCount; i++) {
            const x = i * (barWidth + barSpacing);
            const barHeight = minBarHeight + Math.sin(i * 0.3) * 2;
            const y = centerY - barHeight / 2;

            ctx.fillStyle = '#cbd5e1';
            this.roundRect(ctx, x, y, barWidth, barHeight, barWidth / 2);
            ctx.fill();
        }
    }

    drawProcessingAnimation() {
        if (this.processingAnimation) return;

        let phase = 0;
        const animate = () => {
            if (!this.processingAnimation) return;

            const { ctx, displayWidth, displayHeight, barCount, barSpacing } = this;

            ctx.clearRect(0, 0, displayWidth, displayHeight);

            const totalSpacing = (barCount - 1) * barSpacing;
            const barWidth = (displayWidth - totalSpacing) / barCount;
            const maxBarHeight = displayHeight * 0.5;
            const centerY = displayHeight / 2;

            for (let i = 0; i < barCount; i++) {
                const offset = (i / barCount) * Math.PI * 2 + phase;
                const value = (Math.sin(offset) + 1) / 2;
                const barHeight = 4 + value * maxBarHeight;

                const x = i * (barWidth + barSpacing);
                const y = centerY - barHeight / 2;

                ctx.fillStyle = '#f59e0b';
                this.roundRect(ctx, x, y, barWidth, barHeight, barWidth / 2);
                ctx.fill();
            }

            phase += 0.1;
            requestAnimationFrame(animate);
        };

        this.processingAnimation = true;
        animate();
    }

    stopProcessingAnimation() {
        this.processingAnimation = false;
        this.drawIdleState();
    }

    roundRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
    }

    resize() {
        this.setupCanvas();
        if (!this.isActive) {
            this.drawIdleState();
        }
    }
}

// Handle window resize
window.addEventListener('resize', () => {
    if (window.voiceVisualizer) {
        window.voiceVisualizer.resize();
    }
});
