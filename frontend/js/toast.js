/**
 * M537 Voice Gateway - Toast Notifications
 * Lightweight toast notification system
 */

class ToastManager {
    constructor() {
        this.container = document.getElementById('toastContainer');
        this.toasts = [];
        this.maxToasts = 3;
    }

    /**
     * Show a toast notification
     * @param {string} message - The message to display
     * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in milliseconds (default: 3000)
     */
    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.setAttribute('role', 'alert');

        // Limit number of toasts
        if (this.toasts.length >= this.maxToasts) {
            const oldest = this.toasts.shift();
            oldest.remove();
        }

        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Auto remove
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        // Click to dismiss
        toast.addEventListener('click', () => {
            this.remove(toast);
        });

        return toast;
    }

    remove(toast) {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => {
            const index = this.toasts.indexOf(toast);
            if (index > -1) {
                this.toasts.splice(index, 1);
            }
            toast.remove();
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global toast instance
window.toast = new ToastManager();
