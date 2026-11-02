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
