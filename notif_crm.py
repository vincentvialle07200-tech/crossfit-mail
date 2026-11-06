"""
Alerte « nouveau prospect » du CRM La Salle CrossFit, déposée dans la boîte contact@ (IMAP APPEND, comme le brief).

Le CRM (https://crm-lasallecrossfit.vercel.app) expose /api/leads/recents : horodatage + source des prospects
des 3 derniers jours, SANS aucune donnée personnelle. Pour chaque nouveau prospect, un mail
« 🔥 Nouveau prospect … » arrive dans la boîte de réception avec le lien vers le CRM (nom et téléphone
restent dans le CRM). Rien n'est fait si le CRM envoie déjà ses propres e-mails (emailDirect).

Anti-doublon : en-tête X-CRM-Prospect = horodatage du prospect, recherché dans la boîte avant chaque dépôt,
+ liste des horodatages déjà traités dans l'état (etat/etat.json).
Variables : IMAP_USER, IMAP_PASSWORD. Option : CRM_URL.
"""
import json
import os
import time
import urllib.request
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate
from zoneinfo import ZoneInfo

import tri

CRM = os.environ.get('CRM_URL', 'https://crm-lasallecrossfit.vercel.app')
PARIS = ZoneInfo('Europe/Paris')
FENETRE_PREMIER_PASSAGE = 6 * 3600  # sans état : on ne signale que les prospects des 6 dernières heures


def prospects_recents():
    req = urllib.request.Request(CRM + '/api/leads/recents', headers={'User-Agent': 'crossfit-mail/notif'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def horodatage(iso):
    return datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp()


def main():
    donnees = prospects_recents()
    if donnees.get('emailDirect'):
        print('CRM : e-mails envoyés par le CRM lui-même, rien à faire')
        return
    etat = tri.charger_etat()
    vus = set(etat.get('crm_vus', []))
    maintenant = time.time()
    if 'crm_vus' not in etat:
        limite = maintenant - FENETRE_PREMIER_PASSAGE
        nouveaux = [p for p in donnees.get('prospects', []) if horodatage(p['cree']) >= limite]
    else:
        nouveaux = [p for p in donnees.get('prospects', []) if p['cree'] not in vus]
    if not nouveaux:
        etat['crm_vus'] = sorted(vus | {p['cree'] for p in donnees.get('prospects', [])})[-200:]
        tri.sauver_etat(etat)
        print('CRM : aucun nouveau prospect')
        return

    boite = tri.Boite(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
    deposes = 0
    try:
        boite.selectionner('INBOX')
        for p in nouveaux:
            if boite.chercher('HEADER', 'X-CRM-Prospect', p['cree']):
                vus.add(p['cree'])
                continue
            quand = datetime.fromtimestamp(horodatage(p['cree']), PARIS).strftime('%d/%m à %Hh%M')
            source = p.get('source') or 'Autre'
            msg = EmailMessage()
            msg['From'] = formataddr(('CRM La Salle CrossFit', os.environ['IMAP_USER']))
            msg['To'] = os.environ['IMAP_USER']
            msg['Subject'] = '🔥 Nouveau prospect (%s) — %s' % (source, quand)
            msg['Date'] = formatdate(localtime=True)
            msg['X-CRM-Prospect'] = p['cree']
            msg['X-CRM-LaSalle'] = 'notification'
            msg.set_content('\n'.join([
                'Salut,',
                '',
                'Un nouveau prospect vient d\'arriver dans le CRM (%s, le %s).' % (source, quand),
                '',
                'Rappelle-le vite (dans l\'heure si possible) : c\'est maintenant qu\'il est le plus chaud !',
                'Son nom et son téléphone sont dans l\'onglet Prospects : %s/leads' % CRM,
                '',
                'CRM La Salle CrossFit',
            ]))
            tri.DRY_RUN = os.environ.get('DRY_RUN') == '1'
            boite.ajouter('INBOX', msg, '()')
            vus.add(p['cree'])
            deposes += 1
    finally:
        boite.fermer()
    etat['crm_vus'] = sorted(vus | {p['cree'] for p in donnees.get('prospects', [])})[-200:]
    tri.sauver_etat(etat)
    print('CRM : %d alerte(s) « nouveau prospect » déposée(s)' % deposes)


if __name__ == '__main__':
    main()
