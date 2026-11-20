#!/usr/bin/env python3
"""Fort Énigma — vérifie que chaque fichier local utilisé par le jeu existe bien dans le dossier publié.

    python3 outils/references.py [dossier=.]

Contrôle : images/pages/icônes citées par index.html, fichiers préchargés par le service worker (sw.js),
icônes du manifeste. Échoue (code 1) si un seul manque : image cassée ou hors connexion impossible à installer.
"""
import json, pathlib, re, sys

dossier = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
html = (dossier / "index.html").read_text(encoding="utf-8")
refs = set(re.findall(r'''(?:src|href)=\\?["']((?!https?:|data:|#|mailto|/\.netlify|javascript)[^"'\\?$]+\.(?:png|jpe?g|webp|svg|ico|html|json|webmanifest|txt|xml|avif))''', html))
sw = dossier / "sw.js"
if sw.exists():
    refs |= {f for f in re.findall(r"'(\./[^']+)'", sw.read_text(encoding="utf-8")) if f != "./"}
man = dossier / "manifest.webmanifest"
if man.exists():
    refs |= {i["src"] for i in json.loads(man.read_text(encoding="utf-8")).get("icons", [])}
manque = sorted(r for r in refs if not (dossier / r.lstrip("./").lstrip("/")).exists())
for r in manque:
    print("  ✗ fichier manquant :", r)
print("Références : %d fichiers locaux, %s." % (len(refs), "tous présents" if not manque else "%d manquant(s)" % len(manque)))
sys.exit(1 if manque else 0)
