// Service Worker pour ORLYNE-A12B PWA

const CACHE_NAME = 'orlyne-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/chat.js',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Installation du service worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache ouvert');
                return cache.addAll(urlsToCache);
            })
    );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Stratégie de cache : Network First, fallback to cache
self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Mise en cache de la nouvelle réponse
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(() => {
                // Fallback sur le cache
                return caches.match(event.request);
            })
    );
});

// Gestion des notifications push
self.addEventListener('push', event => {
    const options = {
        body: event.data.text(),
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'open',
                title: 'Ouvrir'
            },
            {
                action: 'close',
                title: 'Fermer'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('ORLYNE', options)
    );
});

// Gestion du clic sur notification
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Background sync pour les messages offline
self.addEventListener('sync', event => {
    if (event.tag === 'sync-messages') {
        event.waitUntil(syncMessages());
    }
});

async function syncMessages() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const requests = await cache.keys();
        
        // Filtrer les requêtes en attente
        const pendingRequests = requests.filter(request => 
            request.url.includes('/api/chat') && 
            request.method === 'POST'
        );
        
        for (const request of pendingRequests) {
            try {
                const response = await fetch(request);
                if (response.ok) {
                    await cache.delete(request);
                }
            } catch (error) {
                console.error('Erreur sync:', error);
            }
        }
    } catch (error) {
        console.error('Erreur sync messages:', error);
    }
}