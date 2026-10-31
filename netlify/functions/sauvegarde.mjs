// ============================================================
// Fort Énigma -- sauvegarde partagée entre appareils
// ------------------------------------------------------------
// Le jeu chiffre la progression DANS LE NAVIGATEUR (AES-GCM) avec une
// clé tirée du « code de voyage » du joueur, puis l'envoie ici. Cette
// fonction ne voit donc jamais ni le code ni la progression en clair :
// elle range un paquet chiffré sous un identifiant opaque (empreinte
// SHA-256 dérivée du code) dans Netlify Blobs, et le rend à qui
// présente le même identifiant.
//
//   GET    ?id=<64 hex>            -> { rev, t, iv, d }  ou 404 { t }
//   PUT    { id, rev, iv, d }      -> { rev, t }         ou 409 si la
//          sauvegarde a changé entre-temps (le jeu refusionne et renvoie)
//   DELETE ?id=<64 hex>            -> { ok }             (oublier en ligne)
//
// Garde-fous : même origine obligatoire pour écrire, JSON uniquement,
// taille bornée, formats stricts, limite de débit, aucune donnée
// sensible dans les erreurs. Rien à configurer : Netlify Blobs est
// fourni avec le site.
// ============================================================

export const config = {
  rateLimit: { windowLimit: 40, windowSize: 60, aggregateBy: ["ip", "domain"] },
};

const MAX_CORPS = 400_000; // octets reçus au plus
const MAX_DONNEES = 360_000; // longueur du paquet chiffré (base64)
const RE_ID = /^[0-9a-f]{64}$/;
const RE_B64 = /^[A-Za-z0-9+/]+={0,2}$/;
const ORIGINES = /^https:\/\/([a-z0-9-]+--)?fort-enigma\.netlify\.app$|^http:\/\/localhost(:\d+)?$/;

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

function origineOk(req) {
  const o = req.headers.get("origin");
  if (!o) return false;
  try {
    if (new URL(req.url).origin === o) return true;
  } catch (e) {}
  return ORIGINES.test(o);
}

let magasinParDefaut = null;
async function magasin() {
  if (!magasinParDefaut) {
    const { getStore } = await import("@netlify/blobs");
    magasinParDefaut = getStore({ name: "sauvegardes", consistency: "strong" });
  }
  return magasinParDefaut;
}

// Traitement isolé (testable avec un faux magasin)
export async function traiter(req, store) {
  const t = Date.now();
  const url = new URL(req.url);

  if (req.method === "GET" || req.method === "DELETE") {
    const id = url.searchParams.get("id") || "";
    if (!RE_ID.test(id)) return json({ erreur: "identifiant invalide" }, 400);
    if (req.method === "DELETE") {
      if (!origineOk(req)) return json({ erreur: "origine refusée" }, 403);
      await store.delete(id);
      return json({ ok: true, t });
    }
    const b = await store.get(id, { type: "json" });
    if (!b) return json({ t }, 404);
    return json({ rev: b.rev | 0, t, iv: b.iv, d: b.d });
  }

  if (req.method !== "PUT") return json({ erreur: "méthode non permise" }, 405);
  if (!origineOk(req)) return json({ erreur: "origine refusée" }, 403);
  if (!/^application\/json\b/i.test(req.headers.get("content-type") || "")) return json({ erreur: "JSON attendu" }, 415);
  const taille = Number(req.headers.get("content-length") || 0);
  if (taille > MAX_CORPS) return json({ erreur: "sauvegarde trop lourde" }, 413);
  const brut = await req.text();
  if (brut.length > MAX_CORPS) return json({ erreur: "sauvegarde trop lourde" }, 413);

  let c;
  try { c = JSON.parse(brut); } catch (e) { return json({ erreur: "JSON invalide" }, 400); }
  if (!c || typeof c !== "object" || Array.isArray(c)) return json({ erreur: "format invalide" }, 400);
  const { id, iv, d } = c;
  const rev = Number.isInteger(c.rev) && c.rev >= 0 ? c.rev : -1;
  if (typeof id !== "string" || !RE_ID.test(id)) return json({ erreur: "identifiant invalide" }, 400);
  if (typeof iv !== "string" || iv.length !== 16 || !RE_B64.test(iv)) return json({ erreur: "format invalide" }, 400);
  if (typeof d !== "string" || !d.length || !RE_B64.test(d)) return json({ erreur: "format invalide" }, 400);
  if (d.length > MAX_DONNEES) return json({ erreur: "sauvegarde trop lourde" }, 413);
  if (rev < 0) return json({ erreur: "révision manquante" }, 400);

  // écriture conditionnelle : on n'écrase jamais une version plus récente
  const actuel = store.getWithMetadata ? await store.getWithMetadata(id, { type: "json" }) : null;
  const courant = actuel && actuel.data ? actuel.data.rev | 0 : 0;
  if (courant !== rev) return json({ erreur: "conflit", rev: courant, t }, 409);
  const nouveau = { rev: courant + 1, iv, d, t };
  const cond = actuel && actuel.etag ? { onlyIfMatch: actuel.etag } : { onlyIfNew: true };
  const res = await store.setJSON(id, nouveau, cond);
  if (res && res.modified === false) return json({ erreur: "conflit", rev: courant, t }, 409);
  return json({ rev: nouveau.rev, t });
}

export default async (req) => {
  try {
    return await traiter(req, await magasin());
  } catch (e) {
    console.error("sauvegarde : échec", e && e.name);
    return json({ erreur: "service momentanément indisponible" }, 503);
  }
};
