"""Audit ResaWod (5/11/2026) : KPI mensuels sur 12 mois + effectifs et conversion des inscrits.
N'affiche QUE des agrégats (journal d'un dépôt public)."""
import os, sys
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brief import kpi_mois
from relances import Segments, ABONNEMENTS, CARNETS, SEANCES_RESTANTES, reservations_depuis

seg = Segments()
r = seg.r

print('== KPI ResaWod par mois (moyennes renvoyées par /reports/kpis)')
fin = date.today().replace(day=1) - timedelta(days=1)
for _ in range(12):
    try:
        k = kpi_mois(r, fin)
        print(fin.strftime('%Y-%m'), ' '.join('%s=%s' % (c, round(v, 2) if isinstance(v, (int, float)) else v) for c, v in sorted(k.items())))
    except Exception as e:
        print(fin.strftime('%Y-%m'), 'erreur', type(e).__name__)
    fin = fin.replace(day=1) - timedelta(days=1)

print('\n== Effectifs actuels')
abo = seg.users(ABONNEMENTS)
car = seg.users(CARNETS)
car_s = seg.users(CARNETS, SEANCES_RESTANTES)
r30 = seg.users(reservations_depuis(30))
r90 = seg.users(reservations_depuis(90))
print('abonnements actifs', len(abo), '| dont réservé sur 30 j', len(set(abo) & set(r30)))
print('carnets actifs', len(car), '| avec séances restantes', len(car_s), '| ayant réservé sur 30 j', len(set(car) & set(r30)))
print('personnes ayant réservé sur 30 j', len(r30), '| sur 90 j', len(r90))
for mid in ABONNEMENTS['id_memberships']:
    n = len(seg.users(dict(ABONNEMENTS, id_memberships=[mid])))
    if n:
        print('  formule', mid, ':', n, 'abonnés actifs')
for vid in CARNETS['id_vouchers']:
    n = len(seg.users(dict(CARNETS, id_vouchers=[vid])))
    if n:
        print('  carnet', vid, ':', n, 'actifs')

print('\n== Inscrits (comptes créés) par fenêtre et ce qu\'ils sont devenus')
deja = set()
prec = {}
for j in (30, 60, 90, 180, 365):
    cree = {"field_identifier": "created_at", "type": 4, "condition": "less_than_x_days_ago", "section": 1, "value": str(j)}
    ins = set(seg.users(cree))
    venus = ins & set(seg.users(cree, reservations_depuis(3650)))
    print('créés sur %3d j : %4d | ont réservé au moins 1 cours %4d | abonnés actifs %3d | carnet actif %3d | réservé sur 30 j %3d' % (
        j, len(ins), len(venus), len(ins & set(abo)), len(ins & set(car)), len(ins & set(r30))))
