"""Cherche un expéditeur / une marque dans tous les dossiers (corbeille comprise).
MOTIF = regex (ex. « fit\\s*(&|and|n|et|-)?\\s*rack »), TEXTE = mot pour la recherche IMAP (ex. « rack »).
RESTAURER=1 : les mails trouvés dans la corbeille reviennent dans la boîte de réception (mot-clé TriIA_info).
Journal = dossier, nombre, domaine expéditeur, catégorie : jamais de sujet ni de nom (dépôt public)."""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tri import Boite  # noqa: E402

motif = re.compile(os.environ['MOTIF'], re.I)
texte = os.environ.get('TEXTE') or os.environ['MOTIF']
boite = Boite(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
try:
    corbeille = boite.special('\\Trash', {'trash', 'corbeille'})
    a_restaurer = []
    for dossier in list(boite.dossiers):
        if '\\noselect' in boite.dossiers[dossier].lower():
            continue
        try:
            boite.selectionner(dossier, lecture_seule=True)
        except Exception:
            continue
        uids = boite.chercher('CHARSET', 'UTF-8', 'TEXT', '"%s"' % texte) if texte else []
        if not uids:
            continue
        data = boite.uid('FETCH', b','.join(uids), '(FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)] BODY.PEEK[TEXT]<0.20000>)')
        trouves = []
        cur = None
        for item in data:
            if isinstance(item, tuple):
                m = re.search(rb'UID (\d+)', item[0])
                if m:
                    cur = {'uid': m.group(1), 'flags': item[0].decode(errors='ignore'), 'txt': ''}
                    trouves.append(cur)
                if cur is not None:
                    cur['txt'] += item[1].decode(errors='ignore')
        ok = [t for t in trouves if motif.search(t['txt'])]
        if not ok:
            continue
        domaines = Counter((re.search(r'From:.*?@([\w.-]+)', t['txt'], re.I | re.S) or [None, '?'])[1].lower() for t in ok)
        cats = Counter((re.search(r'TriIA_(\w+)', t['flags']) or [None, 'non trié'])[1] for t in ok)
        print('%s : %d mail(s) — domaines %s — catégories %s' % (dossier, len(ok), dict(domaines), dict(cats)))
        if dossier == corbeille:
            a_restaurer = [t['uid'] for t in ok]
    if os.environ.get('RESTAURER') == '1' and a_restaurer and corbeille:
        boite.selectionner(corbeille)
        ens = b','.join(a_restaurer)
        boite.uid('STORE', ens, '-FLAGS.SILENT', '(TriIA_pub)')
        boite.uid('STORE', ens, '+FLAGS.SILENT', '(TriIA_info)')
        boite.deplacer(ens, 'INBOX')
        print('Remis dans la boîte de réception : %d' % len(a_restaurer))
finally:
    boite.fermer()
