# Tri IA des mails — La Salle CrossFit

Trie la boîte **contact@lasallecrossfit.fr** (IONOS, IMAP) toutes les 10 min avec Claude Haiku, sur GitHub Actions (gratuit, aucun ordinateur allumé).
Version IMAP du tri THE GYM (`~/the-gym-mail/Code.gs`) : même prompt, même schéma JSON, même règle anti-manipulation.

## Ce que ça fait dans la boîte
| Catégorie | Où | Marquage |
|---|---|---|
| Urgent, À répondre | reste dans la boîte de réception | 🚩 drapeau + brouillon de réponse dans **Brouillons** |
| Compta | `Tri IA/3 Compta` | non lu conservé |
| Info | `Tri IA/4 Info` | non lu conservé |
| Pub & notifs | `Tri IA/5 Pub & notifs` | marqué lu |
| Demande STOP (RGPD) | copie dans `Tri IA/STOP marketing` | à retirer des listes d'envoi |

Le drapeau disparaît quand on répond (depuis le webmail ou une appli mail). **Rien n'est jamais envoyé ni supprimé.**
En cas de panne : un mail « ⚠️ Tri IA des mails en panne » apparaît dans la boîte (1×/jour) + mail GitHub à Vincent.

## Fiche d'infos
Google Doc « La Salle CrossFit — Infos pour le tri IA des mails » : modifiable par les associés, lu avant chaque réponse. Les `[À COMPLÉTER]` ne sont jamais inventés.

## Réglages GitHub (Settings → Secrets and variables → Actions)
- Secrets : `IMAP_PASSWORD`, `ANTHROPIC_API_KEY` (clé « CROSSFIT », plafond 5 €/mois)
- Variables : `IMAP_USER` = contact@lasallecrossfit.fr, `INFOS_URL` = lien d'export texte du Google Doc

## Commandes
- Lancer à la main : onglet **Actions → Tri IA des mails → Run workflow**
- **Arrêt d'urgence** : Actions → Tri IA des mails → ⋯ → **Disable workflow**
- Test local sans rien modifier : `DRY_RUN=1 DETAILS=1 IMAP_USER=… IMAP_PASSWORD=… ANTHROPIC_API_KEY=… python3 tri.py`
- Test du prompt sur mails fictifs : `ANTHROPIC_API_KEY=… python3 test_prompt.py`

Dépôt public (minutes GitHub illimitées) : aucun secret ni donnée de mail dans le code ; les journaux n'affichent que des compteurs.
