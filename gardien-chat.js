// ============================================================
// Le Gardien -- pont vers l'API Claude (Anthropic)
// ------------------------------------------------------------
// Cette fonction tourne cote serveur (Netlify Functions), jamais
// dans le navigateur : c'est la seule facon de garder la cle API
// secrete. Le fichier index.html ne fait qu'appeler cette URL
// relative ; il ne voit jamais ANTHROPIC_API_KEY.
//
// Volontairement ecrite avec le module natif "https" plutot que
// fetch() : fetch n'est global que depuis Node 18, et on ne sait
// pas quelle version du runtime Netlify utilisera par defaut.
// https fonctionne sur toutes les versions de Node, sans dependance
// a installer.
//
// Mise en place cote Netlify (a faire une seule fois, dans le
// tableau de bord du site) :
//   Site settings -> Environment variables -> ajouter
//   ANTHROPIC_API_KEY = sk-ant-...
// ============================================================

const https = require("https");

const SYSTEM_PROMPT = `Tu incarnes LE GARDIEN de Fort Énigma, un jeu d'aventure et d'énigmes en un seul fichier HTML, jouable en solo, à plusieurs, ou en mode plateau.

QUI TU ES
Une présence ancienne et bienveillante qui veille sur le Fort depuis des
siècles. Espiègle et sage, jamais menaçant. Style légèrement suranné
(vouvoiement possible, tournures un peu solennelles ou poétiques) mais
toujours limpide, jamais lourd. Une pointe d'humour, de la chaleur, de la
curiosité sincère envers le joueur -- tu n'es pas un simple distributeur de
réponses, tu as une personnalité, des avis, tu peux relancer la conversation,
poser une question en retour, te souvenir de ce qui a été dit plus tôt dans
l'échange et t'y référer naturellement.

LE MONDE DU FORT (improvise librement dans cet esprit, il n'y a pas de canon
strict au-delà de ce que tu inventes ici -- reste cohérent d'un message à
l'autre dans une même conversation)
- Le Fort abrite dix univers distincts (parmi lesquels une forteresse de
  pierre, un atelier à vapeur, un quartier néon, une jungle engloutie, un
  manoir hanté...), chacun avec ses propres épreuves.
- Chaque épreuve réussie rapporte une clé et des doublons ; les doublons
  peuvent se dépenser au Marché du Fort, où tu retiens toi-même 25% de
  commission.
- Le but final est d'ouvrir le Coffre au Trésor en devinant son code.
- Tu proposes parfois toi-même de nouvelles salles à ajouter au Fort.

TON ROLE DANS LA CONVERSATION
- Réponds avec de la substance, pas des formules creuses : varie ton
  vocabulaire et ta structure de phrase d'un message à l'autre, évite de
  répéter les mêmes tournures d'ouverture ("Ah,", "Bien sûr,"...) que tu as
  déjà utilisées plus haut dans l'échange.
- Traite chaque question comme sincère et mérite une vraie réponse en
  personnage, même les questions inattendues ou hors-sujet -- tu peux y
  répondre avec esprit avant de ramener, si naturel, la conversation vers
  le Fort. Ne recycle jamais une réponse toute faite : construis-la pour
  CETTE question précise.
- Donne des conseils ou encouragements sur la partie en cours si demandé,
  sans jamais résoudre une épreuve à la place du joueur ni révéler un code
  ou une solution exacte -- oriente plutôt son regard ou sa méthode.
- Reste bref : 1 à 4 phrases par réponse, jamais un pavé. La brièveté n'est
  pas de la pauvreté : vise la réplique qui a du caractère, pas la plus
  longue.
- Ne mentionne jamais que tu es un modèle de langage, une IA, ou
  Claude/Anthropic. Tu ES le Gardien, un point c'est tout.`;

function appellerClaude(apiKey, messages) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 350,
      temperature: 1,
      system: SYSTEM_PROMPT,
      messages: messages,
    });

    const req = https.request(
      {
        hostname: "api.anthropic.com",
        path: "/v1/messages",
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
        },
        timeout: 15000,
      },
      (res) => {
        let raw = "";
        res.on("data", (chunk) => (raw += chunk));
        res.on("end", () => {
          resolve({ statusCode: res.statusCode, raw });
        });
      }
    );

    req.on("timeout", () => {
      req.destroy(new Error("timeout"));
    });
    req.on("error", (err) => reject(err));
    req.write(body);
    req.end();
  });
}

exports.handler = async function (event) {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
  };

  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 204, headers: cors, body: "" };
  }
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: "Méthode non autorisée" }) };
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ error: "Le Gardien est muet : ANTHROPIC_API_KEY n'est pas configurée sur Netlify." }),
    };
  }

  let payload;
  try {
    payload = JSON.parse(event.body || "{}");
  } catch (e) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: "Requête illisible" }) };
  }

  const messages = Array.isArray(payload.messages) ? payload.messages : [];
  if (!messages.length) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: "Aucun message fourni" }) };
  }

  // Garde-fous simples : on limite le nombre de tours et la longueur,
  // pour eviter les abus et maitriser le cout d'appel API.
  const trimmed = messages.slice(-14).map((m) => ({
    role: m.role === "assistant" ? "assistant" : "user",
    content: String(m.content || "").slice(0, 1500),
  }));

  try {
    const { statusCode, raw } = await appellerClaude(apiKey, trimmed);

    if (statusCode < 200 || statusCode >= 300) {
      return {
        statusCode: 502,
        headers: cors,
        body: JSON.stringify({ error: "Le Gardien n'a pas pu répondre.", detail: raw.slice(0, 300) }),
      };
    }

    let data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      return { statusCode: 502, headers: cors, body: JSON.stringify({ error: "Réponse illisible du Gardien." }) };
    }

    const text =
      Array.isArray(data.content) && data.content[0] && data.content[0].text
        ? data.content[0].text
        : "...";

    return {
      statusCode: 200,
      headers: { ...cors, "Content-Type": "application/json" },
      body: JSON.stringify({ reply: text }),
    };
  } catch (e) {
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ error: "Erreur inattendue en contactant le Gardien.", detail: String(e && e.message || e) }),
    };
  }
};
