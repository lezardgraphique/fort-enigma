/* Fort Enigma — service worker.
   Le jeu tient dans index.html : on le garde en reserve pour pouvoir
   jouer sans connexion (train, avion, zone blanche).
   - page du jeu : reseau d'abord (les mises a jour arrivent tout de
     suite), la copie en reserve ne sert que hors connexion ;
   - icones et manifeste : reserve d'abord, rafraichie en arriere-plan.
   La meteo (api.open-meteo.com) n'est jamais mise en reserve. */
var RESERVE = 'fort-enigma-v1';
/* la page est rangee sous « ./ » : certains hebergeurs redirigent
   /index.html vers / (Vercel), et une reponse redirigee ne peut pas
   servir de page hors connexion */
var ESSENTIEL = ['./', './manifest.webmanifest', './icones/icone.svg',
                 './icones/icone-192.png', './icones/icone-512.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(RESERVE).then(function (c) { return c.addAll(ESSENTIEL); })
    .then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (cles) {
    return Promise.all(cles.filter(function (k) { return k !== RESERVE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(function (rep) {
      if (rep.ok && !rep.redirected) {
        var copie = rep.clone();
        caches.open(RESERVE).then(function (c) { c.put('./', copie); });
      }
      return rep;
    }).catch(function () {
      return caches.match('./');
    }));
    return;
  }

  e.respondWith(caches.match(req).then(function (enReserve) {
    var reseau = fetch(req).then(function (rep) {
      if (rep.ok) {
        var copie = rep.clone();
        caches.open(RESERVE).then(function (c) { c.put(req, copie); });
      }
      return rep;
    });
    return enReserve || reseau;
  }));
});
