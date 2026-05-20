// Service Worker for Espaço Laika PWA
const CACHE_NAME = 'espaco-laika-v1.0.0';
const STATIC_CACHE = 'espaco-laika-static-v1.0.0';
const DYNAMIC_CACHE = 'espaco-laika-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/css/style.css',
    '/css/animations.css',
    '/js/main.js',
    '/js/utils.js',
    '/assets/logo.svg',
    '/assets/favicon.ico',
    '/manifest.json'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[Service Worker] Installing');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .catch(error => {
                console.error('[Service Worker] Error caching static assets:', error);
            })
    );
    // Force activation
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    // Take control of all clients
    self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Skip cross-origin requests
    if (url.origin !== location.origin) return;

    // Handle API requests differently
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static assets
    if (STATIC_ASSETS.includes(url.pathname) || isStaticAsset(url.pathname)) {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle other requests with cache-first strategy
    event.respondWith(handleDynamicRequest(request));
});

// Handle static asset requests (cache-first)
function handleStaticRequest(request) {
    return caches.match(request)
        .then(response => {
            if (response) {
                return response;
            }

            return fetch(request)
                .then(response => {
                    // Cache successful responses
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(STATIC_CACHE)
                            .then(cache => cache.put(request, responseClone));
                    }
                    return response;
                })
                .catch(() => {
                    // Return offline fallback for HTML pages
                    if (request.headers.get('accept').includes('text/html')) {
                        return caches.match('/index.html');
                    }
                });
        });
}

// Handle dynamic requests (network-first with cache fallback)
function handleDynamicRequest(request) {
    return fetch(request)
        .then(response => {
            // Cache successful responses
            if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(DYNAMIC_CACHE)
                    .then(cache => cache.put(request, responseClone));
            }
            return response;
        })
        .catch(() => {
            // Return from cache if network fails
            return caches.match(request)
                .then(response => {
                    if (response) {
                        return response;
                    }

                    // Return offline fallback for HTML pages
                    if (request.headers.get('accept').includes('text/html')) {
                        return caches.match('/index.html');
                    }
                });
        });
}

// Handle API requests (network-first)
function handleApiRequest(request) {
    return fetch(request)
        .then(response => {
            // Cache successful API responses for offline use
            if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(DYNAMIC_CACHE)
                    .then(cache => cache.put(request, responseClone));
            }
            return response;
        })
        .catch(() => {
            // Return cached API response if available
            return caches.match(request);
        });
}

// Check if URL is a static asset
function isStaticAsset(pathname) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'];
    return staticExtensions.some(ext => pathname.endsWith(ext));
}

// Background sync for form submissions
self.addEventListener('sync', event => {
    console.log('[Service Worker] Background sync triggered:', event.tag);

    if (event.tag === 'contact-form-sync') {
        event.waitUntil(syncContactForm());
    }
});

// Push notifications
self.addEventListener('push', event => {
    console.log('[Service Worker] Push received');

    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const options = {
        body: data.body || 'Nova atualização do Espaço Laika!',
        icon: '/assets/logo.svg',
        badge: '/assets/favicon.ico',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Ver Novidades',
                icon: '/assets/logo.svg'
            },
            {
                action: 'close',
                title: 'Fechar'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || 'Espaço Laika',
            options
        )
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] Notification clicked');

    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Periodic background sync for content updates
self.addEventListener('periodicsync', event => {
    if (event.tag === 'content-sync') {
        event.waitUntil(syncContent());
    }
});

// Sync contact form data
async function syncContactForm() {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const keys = await cache.keys();

        // Find pending form submissions
        const formRequests = keys.filter(request =>
            request.url.includes('/api/contact') &&
            request.method === 'POST'
        );

        for (const request of formRequests) {
            try {
                const response = await fetch(request);
                if (response.ok) {
                    await cache.delete(request);
                    console.log('[Service Worker] Contact form synced successfully');
                }
            } catch (error) {
                console.error('[Service Worker] Failed to sync contact form:', error);
            }
        }
    } catch (error) {
        console.error('[Service Worker] Error in contact form sync:', error);
    }
}

// Sync content updates
async function syncContent() {
    try {
        // Check for content updates
        const response = await fetch('/api/content-updates');
        if (response.ok) {
            const updates = await response.json();

            // Update cache with new content
            const cache = await caches.open(DYNAMIC_CACHE);
            for (const update of updates) {
                await cache.put(update.url, new Response(update.content));
            }

            // Notify clients about updates
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'CONTENT_UPDATED',
                    updates: updates
                });
            });
        }
    } catch (error) {
        console.error('[Service Worker] Error syncing content:', error);
    }
}

// Handle messages from main thread
self.addEventListener('message', event => {
    const { type, data } = event.data;

    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;

        case 'GET_CACHE_SIZE':
            getCacheSize().then(size => {
                event.ports[0].postMessage({ cacheSize: size });
            });
            break;

        case 'CLEAR_CACHE':
            clearAllCaches().then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;

        default:
            console.log('[Service Worker] Unknown message type:', type);
    }
});

// Get total cache size
async function getCacheSize() {
    let totalSize = 0;
    const cacheNames = await caches.keys();

    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();

        for (const request of keys) {
            try {
                const response = await cache.match(request);
                if (response) {
                    const blob = await response.blob();
                    totalSize += blob.size;
                }
            } catch (error) {
                console.error('[Service Worker] Error calculating cache size:', error);
            }
        }
    }

    return totalSize;
}

// Clear all caches
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('[Service Worker] All caches cleared');
}

// Performance monitoring
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'PERFORMANCE_METRIC') {
        // Store performance metrics for analysis
        console.log('[Service Worker] Performance metric received:', event.data.metric);
    }
});