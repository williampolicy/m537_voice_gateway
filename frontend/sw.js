/**
 * M537 Voice Gateway - Service Worker
 * Enables offline support and caching
 */

const CACHE_NAME = 'm537-voice-gateway-v1';
const STATIC_CACHE = 'm537-static-v1';
const API_CACHE = 'm537-api-v1';

// Static assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/css/styles.css',
    '/js/config.js',
    '/js/voice-visualizer.js',
    '/js/voice-input.js',
    '/js/voice-output.js',
    '/js/api-client.js',
    '/js/websocket-client.js',
    '/js/keyboard-shortcuts.js',
    '/js/app.js',
    '/manifest.json'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/health',
    '/api/metrics/json'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('[SW] Static assets cached');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[SW] Failed to cache static assets:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => {
                            return name.startsWith('m537-') &&
                                   name !== STATIC_CACHE &&
                                   name !== API_CACHE;
                        })
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip WebSocket connections
    if (url.protocol === 'ws:' || url.protocol === 'wss:') {
        return;
    }

    // API requests - network first, cache fallback
    if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
        event.respondWith(networkFirstStrategy(event.request, API_CACHE));
        return;
    }

    // Static assets - cache first, network fallback
    event.respondWith(cacheFirstStrategy(event.request, STATIC_CACHE));
});

/**
 * Cache-first strategy for static assets
 */
async function cacheFirstStrategy(request, cacheName) {
    const cached = await caches.match(request);
    if (cached) {
        // Update cache in background
        fetchAndCache(request, cacheName);
        return cached;
    }

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('[SW] Fetch failed:', error);
        return new Response('Offline - content not available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

/**
 * Network-first strategy for API requests
 */
async function networkFirstStrategy(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.log('[SW] Network failed, trying cache');
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }

        // Return offline response for API
        return new Response(JSON.stringify({
            success: false,
            error: {
                code: 'OFFLINE',
                message: '网络不可用，请检查连接'
            },
            offline: true
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Fetch and update cache in background
 */
async function fetchAndCache(request, cacheName) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
    } catch (error) {
        // Silently fail - we already have cached version
    }
}

// Handle messages from main thread
self.addEventListener('message', (event) => {
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data.type === 'CLEAR_CACHE') {
        caches.keys().then((names) => {
            names.forEach((name) => {
                if (name.startsWith('m537-')) {
                    caches.delete(name);
                }
            });
        });
    }
});

// Background sync for offline queries
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-queries') {
        event.waitUntil(syncOfflineQueries());
    }
});

async function syncOfflineQueries() {
    // Implement offline query sync if needed
    console.log('[SW] Syncing offline queries...');
}

// Push notifications (future feature)
self.addEventListener('push', (event) => {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body || 'M537 Voice Gateway',
            icon: '/assets/icons/icon-192x192.png',
            badge: '/assets/icons/icon-72x72.png',
            vibrate: [100, 50, 100],
            data: data.data || {},
            actions: [
                { action: 'view', title: '查看' },
                { action: 'dismiss', title: '忽略' }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title || 'M537 通知', options)
        );
    }
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
