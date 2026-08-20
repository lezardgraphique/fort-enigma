#!/usr/bin/env bash
# ==========================================================================
# Fort Énigma — vérifier puis publier, en une commande.
#
#   ./publier.sh                       vérifie, puis pousse avec un message daté
#   ./publier.sh "mon message"         vérifie, puis pousse avec ce message
#   ./publier.sh --sans-test           pousse sans vérifier (déconseillé)
#   ./publier.sh --test-seul           vérifie et s'arrête là
#
# Le principe : rien n'est poussé si une vérification échoue. C'est ce qui
# évite de republier une régression sans s'en apercevoir.
# ==========================================================================

set -uo pipefail
cd "$(dirname "$0")"

vert()  { printf '\033[32m%b\033[0m\n' "$*"; }
rouge() { printf '\033[31m%b\033[0m\n' "$*"; }
gris()  { printf '\033[2m%s\033[0m\n'  "$*"; }
titre() { printf '\n\033[1m%s\033[0m\n%s\n' "$*" "──────────────────────────────────────"; }

SANS_TEST=0
TEST_SEUL=0
MESSAGE=""
for arg in "$@"; do
  case "$arg" in
    --sans-test) SANS_TEST=1 ;;
    --test-seul) TEST_SEUL=1 ;;
    -h|--help)   sed -n '2,12p' "$0"; exit 0 ;;
    *)           MESSAGE="$arg" ;;
  esac
done

# --------------------------------------------------------------------------
titre "1. Contrôles préalables"

if [ ! -f index.html ]; then
  rouge "✗ index.html est introuvable — lancez le script depuis la racine du dépôt."
  exit 1
fi

POIDS=$(du -m index.html | cut -f1)
echo "  · index.html : ${POIDS} Mo"
if [ "$POIDS" -gt 90 ]; then
  rouge "✗ Le fichier dépasse 90 Mo : GitHub le refusera (limite 100 Mo)."
  exit 1
elif [ "$POIDS" -gt 20 ]; then
  gris "  ⚠ Fichier volumineux : chaque commit en stocke une copie complète."
fi

if ! command -v git >/dev/null 2>&1; then
  rouge "✗ git n'est pas installé."
  exit 1
fi

if [ ! -d .git ]; then
  rouge "✗ Ce dossier n'est pas un dépôt git."
  echo "  Pour l'initialiser :"
  echo "    git init && git branch -M main"
  echo "    git remote add origin https://github.com/<compte>/<depot>.git"
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  rouge "✗ Aucun dépôt distant « origin » n'est configuré."
  echo "    git remote add origin https://github.com/<compte>/<depot>.git"
  exit 1
fi
echo "  · dépôt distant : $(git remote get-url origin)"

# --------------------------------------------------------------------------
if [ "$SANS_TEST" -eq 0 ]; then
  titre "2. Audit du fichier (reparer.py)"
  if command -v python3 >/dev/null 2>&1; then
    if python3 outils/reparer.py index.html; then
      vert "✓ audit passé"
    else
      rouge "✗ L'audit a relevé des défauts — rien n'a été poussé."
      echo "  Pour corriger ce qui est automatisable :"
      echo "    python3 outils/reparer.py index.html --reparer"
      exit 1
    fi
  else
    gris "  python3 absent : audit ignoré."
  fi

  titre "3. Test du jeu (verifier.js)"
  if command -v node >/dev/null 2>&1; then
    if node outils/verifier.js index.html; then
      vert "✓ tests passés"
    else
      rouge "✗ Les tests ont échoué — rien n'a été poussé."
      exit 1
    fi
  else
    gris "  node absent : tests ignorés."
  fi
else
  gris "Vérifications désactivées (--sans-test)."
fi

if [ "$TEST_SEUL" -eq 1 ]; then
  vert "\nVérifications terminées. Rien n'a été poussé (--test-seul)."
  exit 0
fi

# --------------------------------------------------------------------------
titre "4. Envoi vers GitHub"

if [ -z "$(git status --porcelain)" ]; then
  vert "✓ Aucun changement à publier : le dépôt est déjà à jour."
  exit 0
fi

echo "  Fichiers modifiés :"
git status --porcelain | sed 's/^/    /'

[ -z "$MESSAGE" ] && MESSAGE="Mise à jour du jeu — $(date '+%d/%m/%Y %H:%M')"

git add -A
git commit -m "$MESSAGE" >/dev/null || { rouge "✗ Le commit a échoué."; exit 1; }
echo "  · commit : $MESSAGE"

BRANCHE=$(git rev-parse --abbrev-ref HEAD)
if git push origin "$BRANCHE"; then
  vert "\n✓ Publié sur la branche « $BRANCHE »."
  echo
  echo "  Suite :"
  echo "   · GitHub relance la vérification automatiquement (onglet Actions)."
  echo "   · Sur Replit : onglet Git → Pull, puis Deploy."
else
  rouge "✗ L'envoi a échoué."
  echo "  Le commit est conservé en local ; corrigez puis relancez :"
  echo "    git push origin $BRANCHE"
  exit 1
fi
