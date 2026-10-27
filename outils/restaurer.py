"""Une fois (27/10/2026) : sort de la corbeille les « pubs » qui n'en sont pas.
ATHX → boîte de réception ; identifiants / mot de passe / code → Tri IA/4 Info.
Journal = compteurs seulement (dépôt public)."""
import os
import re
import sys
from email import message_from_bytes, policy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tri import Boite, DOSSIERS, protege, texte_mail  # noqa: E402

boite = Boite(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
try:
    corbeille = boite.special('\\Trash', {'trash', 'corbeille'})
    info = boite.chemin(DOSSIERS['info'])
    boite.selectionner(corbeille)
    uids = boite.chercher('KEYWORD', 'TriIA_pub')
    print('Pubs dans la corbeille : %d' % len(uids))
    vers_boite, vers_info = [], []
    for i in range(0, len(uids), 50):
        data = boite.uid('FETCH', b','.join(uids[i:i + 50]), '(BODY.PEEK[])')
        for item in data:
            if not isinstance(item, tuple):
                continue
            m = re.search(rb'UID (\d+)', item[0])
            msg = message_from_bytes(item[1], policy=policy.default)
            entete = ' '.join([str(msg.get('From', '')), str(msg.get('Subject', ''))])
            corps = texte_mail(msg)
            if re.search('athx', entete + ' ' + corps, re.I):
                vers_boite.append(m.group(1))
            elif protege(msg, corps):
                vers_info.append(m.group(1))
    for lot, dest in ((vers_boite, 'INBOX'), (vers_info, info)):
        for i in range(0, len(lot), 100):
            ens = b','.join(lot[i:i + 100])
            boite.uid('STORE', ens, '-FLAGS.SILENT', '(TriIA_pub)')
            boite.uid('STORE', ens, '+FLAGS.SILENT', '(TriIA_info)')
            boite.deplacer(ens, dest)
    print('ATHX remis en boîte de réception : %d' % len(vers_boite))
    print('Identifiants / mots de passe remis dans Tri IA/4 Info : %d' % len(vers_info))
finally:
    boite.fermer()
