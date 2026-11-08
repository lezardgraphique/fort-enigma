// Fort Énigma — dernier post Instagram pour les panneaux de la place.
// Deux fonctions Netlify (une fonction planifiée ne peut pas être appelée par une URL) :
//   instagram.mjs (ce fichier, point d'accès) et instagram-maj.mjs (planifiée, toutes les heures), avec l'API Instagram (connexion Instagram) :
//   GET /.netlify/functions/instagram          → { image, compte, legende, quand, lien }
//   GET /.netlify/functions/instagram?image=1  → la photo elle-même (même origine : la CSP du jeu l'accepte)
// Toutes les heures, la fonction va chercher le dernier post et le garde dans Netlify Blobs :
// le jeu ne parle jamais directement à Instagram et le jeton ne quitte pas Netlify.
//
// Variable d'environnement à créer par le propriétaire dans Netlify (jamais dans le dépôt) :
//   INSTAGRAM_TOKEN : jeton longue durée (60 jours) d'un compte Instagram professionnel
//                     (créateur ou entreprise), avec la permission instagram_business_basic.
// Le jeton est prolongé automatiquement (refresh_access_token) une fois par semaine.
import { getStore } from "@netlify/blobs";

const API = "https://graph.instagram.com";

function depuis(ts) {
  const j = Math.floor((Date.now() - Date.parse(ts)) / 86400000);
  return j <= 0 ? "aujourd’hui" : j === 1 ? "hier" : `il y a ${j} jours`;
}

async function rafraichir(store) {
  const memo = await store.get("jeton", { type: "json" });
  let jeton = memo?.valeur || process.env.INSTAGRAM_TOKEN;
  if (!jeton) throw new Error("INSTAGRAM_TOKEN manquant");
  if (!memo || Date.now() - memo.le > 7 * 86400000) {
    const r = await fetch(`${API}/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(jeton)}`);
    if (r.ok) { jeton = (await r.json()).access_token; await store.setJSON("jeton", { valeur: jeton, le: Date.now() }); }
  }
  return jeton;
}

export async function mettreAJour(store) {
  const jeton = await rafraichir(store);
  const champs = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,username";
  const r = await fetch(`${API}/me/media?fields=${champs}&limit=5&access_token=${encodeURIComponent(jeton)}`);
  if (!r.ok) throw new Error(`Instagram ${r.status}`);
  // le dernier post qui a une image (pour une vidéo : sa miniature)
  const post = (await r.json()).data?.find((m) => m.media_url || m.thumbnail_url);
  if (!post) return;
  const src = post.media_type === "VIDEO" ? post.thumbnail_url : post.media_url;
  const img = await fetch(src);
  if (!img.ok) return;
  await store.set("image", new Uint8Array(await img.arrayBuffer()), { metadata: { type: img.headers.get("content-type") || "image/jpeg" } });
  await store.setJSON("post", {
    compte: post.username || "",
    legende: (post.caption || "").slice(0, 300),
    date: post.timestamp,
    lien: post.permalink,
    v: post.id,
  });
}

export default async (req) => {
  const store = getStore("instagram");
  const url = new URL(req.url);
  if (url.searchParams.has("image")) {
    const b = await store.getWithMetadata("image", { type: "arrayBuffer" });
    if (!b) return new Response("", { status: 404 });
    return new Response(b.data, { headers: { "content-type": b.metadata.type, "cache-control": "public, max-age=3600" } });
  }
  const p = await store.get("post", { type: "json" });
  if (!p) return Response.json({}, { status: 404 });
  return Response.json(
    { image: `/.netlify/functions/instagram?image=${encodeURIComponent(p.v)}`, compte: p.compte, legende: p.legende, quand: depuis(p.date), lien: /^https:\/\/www\.instagram\.com\//.test(p.lien) ? p.lien : "" },
    { headers: { "cache-control": "public, max-age=600" } },
  );
};
