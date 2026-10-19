"""Aperçu du brief avec des données fictives (aucune connexion). Usage : ANTHROPIC_API_KEY=... python3 test_brief.py"""
from datetime import datetime, timedelta
import brief

now = datetime.now(brief.PARIS)
m = lambda s, d, h, b=False: {'sujet': s, 'de': d, 'adresse': 'x@example.com', 'date': now - timedelta(hours=h), 'brouillon': b, 'incomplet': False}
mb = {'urgents': [m('Blessure au WOD de 7h', 'Thomas Martin', 3, True)],
      'a_repondre': [m('Essai Hyrox samedi ?', 'Julie Bernard', 5, True), m('Résiliation abonnement', 'Kevin Roux', 20, True),
                     m('Devis FIT & RACK', 'Audrey Vallejo', 26, True)],
      'compta': [m('Facture Rogue n°48213', 'Rogue', 10)], 'avis': [], 'pubs_24h': 14,
      'stop': [m('Désinscription', 'Sophie Durand', 8)]}
rw = {'ok': True, 'mois_kpi': 'septembre',
      'cours_du_jour': [{'heure': '08:30', 'nom': 'WOD', 'inscrits': 9, 'places': 12}, {'heure': '09:45', 'nom': 'WOD', 'inscrits': 16, 'places': 12},
                        {'heure': '11:00', 'nom': 'HYROX TEAM', 'inscrits': 5, 'places': 12}],
      'expirent_7j': [{'id': '11', 'nom': 'Camille Lantin', 'formule': 'ABONNEMENT 2 SEANCES/SEMAINE sans engagement', 'fin': (now + timedelta(days=1)).strftime('%Y-%m-%d')},
                      {'id': '12', 'nom': 'Oumy Diouf', 'formule': 'ABONNEMENT ILLIMITE sans engagement', 'fin': (now + timedelta(days=5)).strftime('%Y-%m-%d')}],
      'anniversaires': ['Zakaria Yousfi'], 'nouveaux_7j': ['Agathe Gourdin', 'Axel Delaye', 'Lola Fichot'],
      'kpi': {'members': 258, 'members_win': 80, 'members_lost': 26, 'members_churn': 11.71, 'total': 41936, 'active_users': 885},
      'kpi_prec': {'members': 251, 'total': 39800}, 'jamais_venus': [{'id': '30', 'nom': 'Léa Test', 'mobile': '+33600000000', 'email': ''}, {'id': '31', 'nom': 'Hugo Test', 'mobile': '+33611111111', 'email': ''}, {'id': '32', 'nom': 'Nina Test', 'mobile': '', 'email': ''}, {'id': '33', 'nom': 'Paul Test', 'mobile': '+33622222222', 'email': ''}, {'id': '34', 'nom': 'Emma Test', 'mobile': '+33633333333', 'email': ''}], 'mobiles': {'11': '+33644444444', '12': '+33655555555'}, 'relances': {'envoyees': 15, 'revenus': 2, 'en_attente': 15, 'mode': 'brouillons'}}
alertes = brief.calculer_alertes(mb, rw, now)
appels = brief.appels_du_jour(rw, rw['mobiles'], {}, now)
donnees = {'date': brief.jour_fr(now), 'alertes': alertes, 'mails_urgents': [x['sujet'] for x in mb['urgents']],
           'mails_a_repondre': [x['sujet'] + ' — ' + x['de'] for x in mb['a_repondre']], 'factures_24h': [x['sujet'] for x in mb['compta']],
           'resawod': {k: v for k, v in rw.items() if k not in ('jamais_venus', 'mobiles')}, 'leviers_deja_donnes': [], 'appels_deja_prevus': [a['nom'] + ' : ' + a['motif'] for a in appels]}
ia = brief.ia_brief(donnees)
h = brief.rendre({'jour': brief.jour_fr(now), 'boite': mb, 'resawod': rw, 'alertes': alertes, 'ia': ia, 'appels': appels}, now)
open('apercu-brief.html', 'w').write(h)
print(brief.en_texte(h))
