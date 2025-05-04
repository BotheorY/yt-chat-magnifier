// Service Worker for YouTube Chat Magnifier
const CACHE_NAME = 'ytcm-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/yt-chat-magnifier.css',
  '/static/css/yt-emoji.css',
  '/static/css/message-flash.css',
  '/static/js/yt-emoji-parser.js',
  '/static/js/yt-chat-magnifier.js',
  '/static/js/ytcm-style-loader.js',
  '/static/js/register-sw.js',
  '/static/images/favicon/favicon-16x16.png',
  '/static/images/favicon/favicon-32x32.png',
  '/static/images/favicon/favicon-192x192.png',
  '/static/images/favicon/favicon-512x512.png',
  '/static/images/favicon/apple-touch-icon.png',
  '/static/manifest.json'
];

// Helper function to check if a URL exists before caching
const checkUrlExists = async (url) => {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    return response.ok;
  } catch (error) {
    console.error(`Error checking URL ${url}:`, error);
    return false;
  }
};

// Service Worker Installation
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async cache => {
        console.log('Cache opened');
        // Use a more resilient caching approach with URL existence check
        const cachePromises = [];
        
        for (const url of urlsToCache) {
          // First check if the URL exists
          const exists = await checkUrlExists(url);
          
          if (exists) {
            // Only try to cache resources that exist
            cachePromises.push(
              cache.add(url).catch(error => {
                console.error('Failed to cache:', url, error);
                // Continue despite the error
                return Promise.resolve();
              })
            );
          }
        }
        
        return Promise.all(cachePromises);
      })
  );
});

// Service Worker Activation
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Network Request Handling
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return the response from the cache
        if (response) {
          return response;
        }
        
        // Clone the request
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest)
          .then(response => {
            // Check if the response is valid
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              })
              .catch(error => {
                console.error('Failed to cache response for:', event.request.url, error);
              });
            
            return response;
          })
          .catch(error => {
            console.error('Fetch failed:', event.request.url, error);
            // You could return a custom offline page here if needed
            // return caches.match('/offline.html');
            return new Response('Network error occurred', { status: 503, statusText: 'Service Unavailable' });
          });
      })
  );
});