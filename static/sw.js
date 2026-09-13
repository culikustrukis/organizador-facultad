'use strict';

/* Service Worker de Organizador Facultad (PWA técnica, sin diseño).
 *
 * Reglas de seguridad:
 *  - SOLO se cachean recursos estáticos (CSS, JS, imágenes, manifest).
 *  - NUNCA se cachean páginas HTML, respuestas de /api/*, sesiones,
 *    login/logout, datos personales ni avatares de /static/uploads/.
 *  - Las peticiones POST/PUT/DELETE no se interceptan en absoluto.
 *  - Las APIs siguen obteniendo los datos reales desde PostgreSQL/Supabase.
 */

var CACHE_NAME = 'organizador-facultad-static-v1';

var STATIC_PREFIXES = ['/static/css/', '/static/js/', '/static/img/'];
var STATIC_EXACT = ['/manifest.json'];
var FONT_ORIGINS = ['https://fonts.googleapis.com', 'https://fonts.gstatic.com'];

var PRECACHE = [
  '/manifest.json',
  '/static/css/tailwind.css',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/auth.js',
  '/static/img/logo.svg',
  '/static/img/avatar.svg',
  '/static/img/icons/icon-192.png',
  '/static/img/icons/icon-512.png'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then(function (cache) { return cache.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches
      .keys()
      .then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) { return key !== CACHE_NAME; })
            .map(function (key) { return caches.delete(key); })
        );
      })
      .then(function () { return self.clients.claim(); })
  );
});

function isStaticAsset(url) {
  var path = url.pathname;
  for (var i = 0; i < STATIC_PREFIXES.length; i++) {
    if (path.indexOf(STATIC_PREFIXES[i]) === 0) return true;
  }
  for (var j = 0; j < STATIC_EXACT.length; j++) {
    if (path === STATIC_EXACT[j]) return true;
  }
  return false;
}

function cacheFirstWithUpdate(request, cache) {
  return caches.match(request).then(function (cached) {
    var network = fetch(request)
      .then(function (response) {
        if (response && response.ok) {
          var copy = response.clone();
          cache.put(request, copy);
        }
        return response;
      })
      .catch(function () { return cached; });
    return cached || network;
  });
}

self.addEventListener('fetch', function (event) {
  var request = event.request;

  if (request.method !== 'GET') return;

  var url = new URL(request.url);

  /* Navegación: siempre en red, nunca se sirve HTML cacheado. */
  if (request.mode === 'navigate') return;

  /* Fuentes de Google: cache-first con actualización en segundo plano. */
  if (FONT_ORIGINS.indexOf(url.origin) !== -1) {
    event.respondWith(
      caches.open(CACHE_NAME).then(function (cache) {
        return cacheFirstWithUpdate(request, cache);
      })
    );
    return;
  }

  /* Recursos estáticos propios: network-first, respaldo a caché solo offline. */
  if (url.origin === self.location.origin && isStaticAsset(url)) {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          if (response && response.ok) {
            var copy = response.clone();
            caches.open(CACHE_NAME).then(function (cache) { cache.put(request, copy); });
          }
          return response;
        })
        .catch(function () { return caches.match(request); })
    );
    return;
  }

  /* Todo lo demás (APIs, HTML, uploads, etc.): comportamiento normal. */
});