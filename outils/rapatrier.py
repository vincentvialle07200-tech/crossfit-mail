"""Remet dans la boîte de réception les mails rangés dans Tri IA/3 Compta et 4 Info depuis JOURS jours
(28/10/2026 : seules les pubs quittent la boîte de réception). Journal = compteurs seulement."""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tri import Boite, DOSSIERS  # noqa: E402

jours = int(os.environ.get('JOURS_RAPATRIER') or 60)
depuis = (datetime.now() - timedelta(days=jours)).strftime('%d-%b-%Y')
boite = Boite(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
try:
    for k in ('compta', 'info'):
        dossier = boite.chemin(DOSSIERS[k])
        if dossier not in boite.dossiers:
            continue
        boite.selectionner(dossier)
        uids = boite.chercher('ALL') if jours >= 3650 else boite.chercher('SINCE', depuis)
        for i in range(0, len(uids), 200):
            boite.deplacer(b','.join(uids[i:i + 200]), 'INBOX')
        reste = len(boite.chercher('ALL'))
        print('%s : %d remis en boîte de réception, %d plus anciens restent' % (DOSSIERS[k], len(uids), reste))
finally:
    boite.fermer()
