/* Fort Énigma — service worker : le jeu reste jouable sans connexion.
   - La page du jeu : réseau d'abord (pour recevoir les mises à jour), copie
     en cache en repli quand il n'y a pas de réseau.
   - Icônes et manifeste : cache d'abord, rafraîchis en arrière-plan.
   - Météo, géolocalisation et chat du Gardien : jamais mis en cache, le jeu
     a déjà ses solutions de repli hors connexion. */
const VERSION = 'fort-enigma-v7';
const NOYAU = ['./', './index.html', './manifest.webmanifest', './icone-192.png', './icone-512.png', './icone-masquable-512.png', './favicon.ico', './favicon-32.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(VERSION)
      .then((c) => Promise.all(NOYAU.map((u) => c.add(u).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((cles) => Promise.all(cles.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function avecDelai(promesse, ms) {
  return new Promise((ok, ko) => {
    const t = setTimeout(() => ko(new Error('délai')), ms);
    promesse.then((r) => { clearTimeout(t); ok(r); }, (e) => { clearTimeout(t); ko(e); });
  });
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;          // API externes : réseau seul
  if (url.pathname.startsWith('/.netlify/') || url.pathname.startsWith('/api/')) return; // fonctions : réseau seul

  if (req.mode === 'navigate' || url.pathname.endsWith('/index.html')) {
    e.respondWith(
      avecDelai(fetch(req), 5000)
        .then((rep) => {
          if (rep && rep.ok) { const copie = rep.clone(); caches.open(VERSION).then((c) => c.put('./index.html', copie)); }
          return rep;
        })
        .catch(() => caches.match('./index.html').then((r) => r || caches.match('./')))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((enCache) => {
      const reseau = fetch(req).then((rep) => {
        if (rep && rep.ok) { const copie = rep.clone(); caches.open(VERSION).then((c) => c.put(req, copie)); }
        return rep;
      }).catch(() => enCache);
      return enCache || reseau;
    })
  );
});
