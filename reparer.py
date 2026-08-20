#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fort Énigma — auditeur et réparateur automatique du fichier de jeu.

    python3 reparer.py index.html            # audit seul (ne modifie rien)
    python3 reparer.py index.html --reparer  # applique les corrections

Ce script travaille sur le FICHIER, hors navigateur. Il connaît les pannes
déjà rencontrées sur ce projet et sait les détecter — et, pour la plupart,
les corriger seul. Chaque règle explique ce qu'elle cherche et pourquoi.

Il ne prétend pas corriger « parfaitement » : il vérifie une liste fermée de
défauts connus. Ce qu'il ne sait pas voir, il ne le voit pas — d'où le
complément verifier.js, qui teste le jeu en conditions réelles.
"""

import re
import sys
import shutil
import datetime

# --------------------------------------------------------------------------
# Chaque règle : (identifiant, description, détection, correction|None)
# La détection renvoie une liste de constats. La correction renvoie le
# nouveau contenu, ou None si la règle n'est pas réparable automatiquement.
# --------------------------------------------------------------------------


def d_commentaire_css_orphelin(txt):
    """Un commentaire /* */ hors de toute balise <style> s'affiche comme du
    texte et occupe de la place dans la page (bug déjà rencontré : 168 px)."""
    masque = list(txt)
    for m in re.finditer(r"<(style|script)\b[^>]*>.*?</\1>", txt, re.S | re.I):
        for i in range(m.start(), m.end()):
            masque[i] = " "
    return [
        f"commentaire CSS hors <style> à l'offset {m.start()} "
        f"({txt[m.start():m.start()+48].strip()!r}…)"
        for m in re.finditer(r"/\*.*?\*/", "".join(masque), re.S)
    ]


def r_commentaire_css_orphelin(txt):
    masque = list(txt)
    for m in re.finditer(r"<(style|script)\b[^>]*>.*?</\1>", txt, re.S | re.I):
        for i in range(m.start(), m.end()):
            masque[i] = " "
    for m in reversed(list(re.finditer(r"/\*.*?\*/", "".join(masque), re.S))):
        txt = txt[:m.start()] + txt[m.end():]
    return txt


def d_fond_etire(txt):
    """background-size:100% 100% déforme l'image (ratio forcé) au lieu de la
    recadrer. C'est ce qui écrasait les décors d'univers."""
    constats = []
    for m in re.finditer(r"[^{};]{0,90}background-size:\s*100%\s+100%", txt):
        bloc = m.group(0)
        if any(k in bloc for k in ("roomLayer", "hero-quai", "decor", "scene")):
            constats.append(f"décor étiré (background-size:100% 100%) : {bloc.strip()[-60:]!r}")
    return constats


def r_fond_etire(txt):
    def remplace(m):
        bloc = m.group(0)
        if any(k in bloc for k in ("roomLayer", "hero-quai", "decor", "scene")):
            return bloc.replace("100% 100%", "cover")
        return bloc
    return re.sub(r"[^{};]{0,90}background-size:\s*100%\s+100%", remplace, txt)


def d_fond_page_clair(txt):
    """Sans fond sombre sur html, une visionneuse intégrée laisse apparaître
    du blanc entre deux peintures : c'est perçu comme un clignotement."""
    if re.search(r"html\s*\{[^}]*background-color:\s*#0", txt):
        return []
    return ["l'élément html n'a pas de fond sombre déclaré (risque de flash blanc)"]


def d_theme_sombre(txt):
    if "color-scheme:dark" in txt.replace(" ", ""):
        return []
    return ["color-scheme:dark non déclaré (flash clair possible au chargement)"]


def d_balises(txt):
    """Balises <style>/<script> non refermées : tout le reste de la page
    peut cesser de fonctionner."""
    constats = []
    for balise in ("style", "script"):
        ouv = len(re.findall(rf"<{balise}\b", txt, re.I))
        fer = len(re.findall(rf"</{balise}>", txt, re.I))
        if ouv != fer:
            constats.append(f"<{balise}> : {ouv} ouverte(s) pour {fer} fermée(s)")
    for balise in ("body", "html", "head"):
        if len(re.findall(rf"</{balise}>", txt, re.I)) != 1:
            constats.append(f"</{balise}> doit apparaître exactement une fois")
    return constats


def d_accolades(txt):
    """Déséquilibre d'accolades dans un bloc <script> : erreur de syntaxe.

    Attention : on retire aussi les littéraux d'expression régulière, sinon
    un motif comme /\\s{2,}/ fausse le comptage (faux positif constaté)."""
    constats = []
    for i, m in enumerate(re.finditer(r"<script[^>]*>(.*?)</script>", txt, re.S)):
        code = m.group(1)
        sans = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`'
                      r"|//[^\n]*|/\*.*?\*/", "", code, flags=re.S)
        # littéraux d'expression régulière : /.../ précédé d'un opérateur
        sans = re.sub(r"(?<=[=(,:!&|?{;\[\s])/(?:\\.|\[(?:\\.|[^\]\\])*\]|[^/\\\n])+/[gimsuy]*",
                      "", sans)
        ecart = sans.count("{") - sans.count("}")
        if ecart:
            constats.append(f"script #{i + 1} : {ecart:+d} accolade(s) non appariée(s)")
    return constats


def d_important_excessif(txt):
    """Trop de !important rend le fichier difficile à faire évoluer : chaque
    correctif doit surenchérir sur le précédent. Signal, pas erreur."""
    n = txt.count("!important")
    return [f"{n} occurrences de !important (au-delà de 1200, la cascade devient fragile)"] if n > 1200 else []


def d_poids(txt):
    mo = len(txt.encode("utf-8")) / (1024 * 1024)
    return [f"fichier de {mo:.1f} Mo (au-delà de 12 Mo, le chargement mobile souffre)"] if mo > 12 else []


def d_intervalles(txt):
    """Un setInterval très court qui écrit dans le DOM hache la réactivité
    au toucher (défaut déjà rencontré : la carte réécrite 50 fois/s)."""
    constats = []
    for m in re.finditer(r"(.{0,40})setInterval\([^,]{0,80},\s*(\d{1,4})\s*\)", txt):
        avant, ms = m.group(1), int(m.group(2))
        if not ms or ms >= 200:
            continue
        # un minuteur dont l'identifiant est conservé sera arrêté plus tard
        # (animation courte) : ce n'est pas une boucle permanente.
        if re.search(r"(=|push\(|\bvar\b|\blet\b|\bconst\b)\s*$", avant):
            continue
        constats.append(f"setInterval permanent toutes les {ms} ms — cadence très élevée")
    return constats


REGLES = [
    ("commentaire-css", "commentaire CSS hors <style>", d_commentaire_css_orphelin, r_commentaire_css_orphelin),
    ("decor-etire", "décor déformé par background-size:100% 100%", d_fond_etire, r_fond_etire),
    ("fond-page", "fond de page clair (clignotement)", d_fond_page_clair, None),
    ("theme-sombre", "color-scheme non déclaré", d_theme_sombre, None),
    ("balises", "balises non appariées", d_balises, None),
    ("accolades", "accolades déséquilibrées dans un script", d_accolades, None),
    ("cadence", "minuteur trop rapide", d_intervalles, None),
    ("important", "surcharge de !important", d_important_excessif, None),
    ("poids", "poids du fichier", d_poids, None),
]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    chemin = sys.argv[1]
    reparer = "--reparer" in sys.argv

    try:
        txt = open(chemin, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"Impossible de lire {chemin} : {e}")
        return 2

    origine = txt
    print(f"Audit de {chemin}\n" + "─" * 46)

    total, corriges, bloquants = 0, 0, 0
    for cle, titre, detecte, repare in REGLES:
        constats = detecte(txt)
        if not constats:
            print(f"  ✓ {titre}")
            continue
        total += len(constats)
        reparable = repare is not None
        if not reparable:
            bloquants += len(constats)
        print(f"  ✗ {titre} — {len(constats)} constat(s)"
              + ("" if reparable else "  [correction manuelle]"))
        for c in constats[:4]:
            print(f"      · {c}")
        if len(constats) > 4:
            print(f"      · … {len(constats) - 4} de plus")
        if reparer and reparable:
            txt = repare(txt)
            reste = detecte(txt)
            corriges += len(constats) - len(reste)
            print(f"      → corrigé automatiquement ({len(constats) - len(reste)})")

    print("─" * 46)
    if total == 0:
        print("Aucun défaut connu détecté.")
        return 0

    if reparer and txt != origine:
        horo = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        sauve = f"{chemin}.avant-{horo}.bak"
        shutil.copy2(chemin, sauve)
        open(chemin, "w", encoding="utf-8").write(txt)
        print(f"{corriges} correction(s) appliquée(s). Sauvegarde : {sauve}")
    elif reparer:
        print("Rien à corriger automatiquement.")
    else:
        print(f"{total} constat(s). Relancez avec --reparer pour appliquer ce qui est automatisable.")

    if bloquants:
        print(f"{bloquants} point(s) demandent une intervention manuelle.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
