self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('mgs-cache').then((cache) => {
      return cache.addAll([
        '/',
        '/static/css/styles.css',
        '/static/js/scripts.js',
        '/static/nalozi/manifest.json'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
