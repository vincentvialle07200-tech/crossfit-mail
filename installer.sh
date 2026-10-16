#!/bin/zsh
# Installation GitHub du tri IA CrossFit — à lancer une fois depuis ~/crossfit-mail
set -e
REPO=vincentvialle07200-tech/crossfit-mail
DOC=1rMiDedCaHIw_qB2aviMkU7SQnjnrLEIjUNye99iOm4E

echo "\n1/4 Connexion GitHub (compte vincentvialle07200-tech)"
gh auth status -h github.com >/dev/null 2>&1 && gh auth refresh -h github.com -s workflow || gh auth login -h github.com -p https -w -s workflow

echo "\n2/4 Envoi du code"
git push -q "https://x-access-token:$(gh auth token)@github.com/$REPO.git" main
git branch -q -u origin/main 2>/dev/null || true

echo "\n3/4 Réglages"
gh variable set IMAP_USER -R $REPO -b contact@lasallecrossfit.fr
gh variable set INFOS_URL -R $REPO -b "https://docs.google.com/document/d/$DOC/export?format=txt"

echo "\n4/4 Secrets (ce que tu colles reste invisible, c'est normal)"
echo "→ Colle le MOT DE PASSE IONOS de contact@lasallecrossfit.fr puis Entrée :"
gh secret set IMAP_PASSWORD -R $REPO
echo "→ Colle la CLÉ API « CROSSFIT » (sk-ant-…) puis Entrée :"
gh secret set ANTHROPIC_API_KEY -R $REPO

echo "\n✅ Terminé. Tu peux revenir dans Claude et écrire « c'est fait »."
