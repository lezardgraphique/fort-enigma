// Fort Énigma — rafraîchit toutes les heures le dernier post Instagram.
import { getStore } from "@netlify/blobs";
import { mettreAJour } from "./instagram.mjs";

export const config = { schedule: "@hourly" };

export default async () => {
  try { await mettreAJour(getStore("instagram")); } catch (e) { console.error(e.message); }
  return new Response("ok");
};
