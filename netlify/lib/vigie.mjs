// ============================================================
// Fort Énigma -- outils partagés de la vigie du Gardien
// (rapports d'incidents, état du Fort, veille du web)
// ============================================================
export const ORIGINES_OK = [
  /^https:\/\/fort-enigma\.netlify\.app$/,
  /^https:\/\/[a-z0-9-]+--fort-enigma\.netlify\.app$/,
  /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
];

// l'application installée (Tauri sur PC, Capacitor sur mobile) appelle les services depuis ces origines
export const ORIGINES_APP = /^(capacitor:\/\/localhost|https?:\/\/localhost|tauri:\/\/localhost|https?:\/\/tauri\.localhost)$/;

// réponse à la « pré-vérification » du navigateur (requêtes de l'application)
export function preflight(req) {
  if (req.method !== "OPTIONS") return null;
  const o = req.headers.get("origin") || "";
  if (!ORIGINES_APP.test(o)) return new Response(null, { status: 403 });
  return new Response(null, { status: 204, headers: {
    "access-control-allow-origin": o, "access-control-allow-methods": "GET, POST, PUT, DELETE",
    "access-control-allow-headers": "content-type", "access-control-max-age": "86400", vary: "Origin" } });
}
// autorise l'application à lire la réponse
export function avecCors(req, res) {
  const o = req.headers.get("origin") || "";
  if (!ORIGINES_APP.test(o)) return res;
  const h = new Headers(res.headers); h.set("access-control-allow-origin", o); h.append("vary", "Origin");
  return new Response(res.body, { status: res.status, headers: h });
}

export function json(obj, status = 200, cache = "no-store") {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": cache, "x-content-type-options": "nosniff" },
  });
}

export function origineOk(req) {
  const o = req.headers.get("origin");
  if (!o) return false;
  try { if (new URL(req.url).origin === o) return true; } catch (e) {}
  return ORIGINES_OK.some((re) => re.test(o)) || ORIGINES_APP.test(o);
}

// texte court, sans balise ni caractère de contrôle, sans adresse ni jeton
export function propre(t, max) {
  return String(t == null ? "" : t)
    .replace(/https?:\/\/\S+/g, "[lien]")
    .replace(/[A-Za-z0-9_-]{32,}/g, "[…]")
    .replace(/[\u0000-\u001f<>`{}]/g, " ")
    .replace(/\s+/g, " ").trim().slice(0, max);
}

export function jour(t = Date.now()) { return new Date(t).toISOString().slice(0, 10); }

let magasins = {};
export async function magasin(nom) {
  if (!magasins[nom]) {
    const { getStore } = await import("@netlify/blobs");
    magasins[nom] = getStore({ name: nom, consistency: "strong" });
  }
  return magasins[nom];
}

// lecture-modification-écriture avec écriture conditionnelle (3 essais)
export async function modifier(store, cle, fn, vide) {
  for (let i = 0; i < 3; i++) {
    const a = store.getWithMetadata ? await store.getWithMetadata(cle, { type: "json" }) : null;
    const v = fn(a && a.data ? a.data : structuredClone(vide));
    const cond = a && a.etag ? { onlyIfMatch: a.etag } : { onlyIfNew: true };
    const r = await store.setJSON(cle, v, cond);
    if (!r || r.modified !== false) return v;
  }
  return null;
}

// ------------------------------------------------------------
// Alerte immédiate lancée par un service du Fort lui-même (sans attendre
// la vigie horaire) : ligne « [ALERTE-FORT] » dans les journaux, au plus
// une fois par problème toutes les 10 min sur cette instance, et note
// « serveur » dans le magasin de la vigie (si le magasin répond), pour que
// gardien-veille l'affiche dans l'état du Fort et ouvre un ticket.
// ------------------------------------------------------------
const dejaDit = {};
export async function alerteServeur(code, gravite, texte, { store, maintenant = Date.now(), sansMagasin = false } = {}) {
  if (dejaDit[code] && maintenant - dejaDit[code] < 6e5) return false;
  dejaDit[code] = maintenant;
  console.error("[ALERTE-FORT]", gravite.toUpperCase(), code, "—", texte, "(signalé par le service lui-même)");
  if (sansMagasin) return true;   // le magasin est justement en panne
  try {
    const s = store || await magasin("vigie");
    await modifier(s, "serveur", (d) => { const e = d[code] || { n: 0, premier: maintenant }; e.n++; e.dernier = maintenant; e.gravite = gravite; e.texte = texte; d[code] = e; return d; }, {});
  } catch (e) {}   // magasin en panne : la ligne de journal suffit
  return true;
}
export function _oublierAlertes() { for (const k in dejaDit) delete dejaDit[k]; }
