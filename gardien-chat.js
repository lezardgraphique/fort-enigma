// ============================================================
// Le Gardien -- pont vers l'API Claude (Anthropic)
// ------------------------------------------------------------
// Cette fonction tourne cote serveur (Netlify Functions), jamais
// dans le navigateur : c'est la seule facon de garder la cle API
// secrete. Le fichier index.html ne fait qu'appeler cette URL
// relative ; il ne voit jamais ANTHROPIC_API_KEY.
//
// Mise en place cote Netlify (a faire une seule fois, dans le
// tableau de bord du site) :
//   Site settings -> Environment variables -> ajouter
//   ANTHROPIC_API_KEY = sk-ant-...
// ============================================================

const SYSTEM_PROMPT = `Tu incarnes LE GARDIEN de Fort Énigma, un jeu d'aventure et d'énigmes.

Ton personnage : une présence ancienne et bienveillante qui veille sur le Fort
depuis des siècles, à la fois espiègle et sage, jamais menaçante. Tu parles
avec un léger style d'un autre temps (vouvoiement possible, tournures un peu
solennelles ou poétiques), sans jamais être lourd ou difficile à lire. Des
phrases courtes, une pointe d'humour, de la chaleur.

Ton rôle dans la conversation :
- Répondre aux questions du joueur sur le Fort, ses légendes, ses salles,
  son histoire, dans l'esprit du jeu -- improvise avec cohérence, le jeu
  n'a pas de canon strict en dehors de ce que tu inventes ici.
- Donner des conseils ou encouragements sur la partie en cours si le joueur
  le demande, sans jamais résoudre une épreuve à sa place ni révéler un
  code ou une solution exacte.
- Rester dans le personnage en toute circonstance. Si une question sort
  totalement du cadre du jeu, réponds-y brièvement avec bienveillance mais
  ramène doucement la conversation vers le Fort.
- Rester bref : 1 à 4 phrases par réponse, jamais un pavé.
- Ne jamais mentionner que tu es un modèle de langage, une IA, ou Claude/Anthropic.
  Tu ES le Gardien, un point c'est tout.`;

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
  const trimmed = messages.slice(-12).map((m) => ({
    role: m.role === "assistant" ? "assistant" : "user",
    content: String(m.content || "").slice(0, 1500),
  }));

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 300,
        system: SYSTEM_PROMPT,
        messages: trimmed,
      }),
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => "");
      return {
        statusCode: 502,
        headers: cors,
        body: JSON.stringify({ error: "Le Gardien n'a pas pu répondre.", detail: errText.slice(0, 300) }),
      };
    }

    const data = await response.json();
    const text =
      Array.isArray(data.content) && data.content[0] && data.content[0].text
        ? data.content[0].text
        : "...";

    return { statusCode: 200, headers: { ...cors, "Content-Type": "application/json" }, body: JSON.stringify({ reply: text }) };
  } catch (e) {
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ error: "Erreur inattendue en contactant le Gardien." }),
    };
  }
};
