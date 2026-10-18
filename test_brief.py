"""Aperçu du brief avec des données fictives (aucune connexion). Usage : ANTHROPIC_API_KEY=... python3 test_brief.py"""
from datetime import datetime, timedelta
import brief

now = datetime.now(brief.PARIS)
m = lambda s, d, h, b=False: {'sujet': s, 'de': d, 'adresse': 'x@example.com', 'date': now - timedelta(hours=h), 'brouillon': b}
mb = {'urgents': [m('Blessure au WOD de 7h', 'Thomas Martin', 3, True)],
      'a_repondre': [m('Essai Hyrox samedi ?', 'Julie Bernard', 5, True), m('Résiliation abonnement', 'Kevin Roux', 20, True),
                     m('Devis FIT & RACK', 'Audrey Vallejo', 26, True)],
      'compta': [m('Facture Rogue n°48213', 'Rogue', 10)], 'avis': [], 'pubs_24h': 14,
      'stop': [m('Désinscription', 'Sophie Durand', 8)]}
rw = {'ok': True, 'mois_kpi': 'septembre',
      'cours_du_jour': [{'heure': '08:30', 'nom': 'WOD', 'inscrits': 9, 'places': 12}, {'heure': '09:45', 'nom': 'WOD', 'inscrits': 16, 'places': 12},
                        {'heure': '11:00', 'nom': 'HYROX TEAM', 'inscrits': 5, 'places': 12}],
      'expirent_7j': [{'nom': 'Camille Lantin', 'formule': 'ABONNEMENT 2 SEANCES/SEMAINE sans engagement', 'fin': '2026-10-19'},
                      {'nom': 'Oumy Diouf', 'formule': 'ABONNEMENT ILLIMITE sans engagement', 'fin': '2026-10-20'}],
      'anniversaires': ['Zakaria Yousfi'], 'nouveaux_7j': ['Agathe Gourdin', 'Axel Delaye', 'Lola Fichot'],
      'kpi': {'members': 258, 'members_win': 80, 'members_lost': 26, 'members_churn': 11.71, 'total': 41936, 'active_users': 885, 'created_users': 78}}
date = 'samedi 18 octobre 2026'
donnees = {'date': date, 'mails_urgents': [x['sujet'] for x in mb['urgents']], 'mails_a_repondre': [x['sujet'] + ' — ' + x['de'] for x in mb['a_repondre']],
           'factures_24h': [x['sujet'] for x in mb['compta']], 'avis_google_24h': [], 'resawod': rw}
p, c = brief.priorites_ia(donnees)
print('PRIORITÉS', p, '\nCONSTATS', c)
open('apercu-brief.html', 'w').write(brief.rendre({'date': date, 'boite': mb, 'resawod': rw, 'priorites': p, 'constats': c}, now))
print('apercu-brief.html écrit')
