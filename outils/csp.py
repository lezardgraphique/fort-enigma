#!/usr/bin/env python3
"""Fort Énigma — politique de sécurité (CSP) stricte pour les scripts.

Chaque script en ligne d'index.html est autorisé par son empreinte SHA-256 :
plus de 'unsafe-inline' pour les scripts, donc un script injecté (XSS) ne s'exécute pas.

    python3 outils/csp.py            # recalcule les empreintes (index.html + netlify.toml)
    python3 outils/csp.py --verifier # échoue si une empreinte ne correspond plus

À lancer APRÈS toute modification d'index.html (dont la version du jeu, qui vit dans un script).
"""
import base64, hashlib, pathlib, re, sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
INDEX = RACINE / "index.html"
TOML = RACINE / "netlify.toml"

SCRIPT = re.compile(rb"<script(?P<attr>[^>]*)>(?P<corps>.*?)</script>", re.S)
TYPES_DONNEES = re.compile(rb"""type\s*=\s*["']?(application/(ld\+)?json|text/template)""", re.I)


def empreintes(octets):
    vues, liste = set(), []
    for m in SCRIPT.finditer(octets):
        if b"src=" in m.group("attr") or TYPES_DONNEES.search(m.group("attr")):
            continue
        h = "'sha256-" + base64.b64encode(hashlib.sha256(m.group("corps")).digest()).decode() + "'"
        if h not in vues:
            vues.add(h); liste.append(h)
    return liste


def avec_scripts(csp, liste):
    return re.sub(r"script-src [^;]*", "script-src " + " ".join(liste), csp, count=1)


def main():
    verifier = "--verifier" in sys.argv
    octets = INDEX.read_bytes()
    liste = empreintes(octets)
    texte = octets.decode("utf-8")
    meta = re.search(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")', texte)
    toml = TOML.read_text(encoding="utf-8")
    entete = re.search(r'(Content-Security-Policy = ")([^"]*)(")', toml)
    if not meta or not entete:
        sys.exit("CSP introuvable dans index.html ou netlify.toml")
    nouvelle_meta, nouvel_entete = avec_scripts(meta.group(2), liste), avec_scripts(entete.group(2), liste)
    if verifier:
        ok = nouvelle_meta == meta.group(2) and nouvel_entete == entete.group(2) and "unsafe-inline" not in re.search(r"script-src [^;]*", meta.group(2)).group(0)
        print(("CSP : %d scripts signés, empreintes à jour." % len(liste)) if ok else "CSP : empreintes périmées — lance python3 outils/csp.py")
        sys.exit(0 if ok else 1)
    texte = texte[:meta.start(2)] + nouvelle_meta + texte[meta.end(2):]
    toml = toml[:entete.start(2)] + nouvel_entete + toml[entete.end(2):]
    INDEX.write_bytes(texte.encode("utf-8"))
    TOML.write_text(toml, encoding="utf-8")
    print("CSP : %d scripts signés (index.html + netlify.toml)." % len(liste))


if __name__ == "__main__":
    main()
