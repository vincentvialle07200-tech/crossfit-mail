"""Export ResaWod CHIFFRÉ pour croiser les leads Meta en local (5/11/2026).
Écrit export.json (comptes + statut) puis le workflow le chiffre avec EXPORT_KEY avant de le publier en artefact
(1 jour). Le journal n'affiche que des totaux : le dépôt est public."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from relances import Segments, ABONNEMENTS, CARNETS, SEANCES_RESTANTES, reservations_depuis

seg = Segments()
def cree(j):
    return {"field_identifier": "created_at", "type": 4, "condition": "less_than_x_days_ago", "section": 1, "value": str(j)}
tous = seg.users(cree(3650))
venus = set(seg.users(cree(3650), reservations_depuis(3650)))
r30 = set(seg.users(reservations_depuis(30)))
abo = set(seg.users(ABONNEMENTS))
car = set(seg.users(CARNETS))
car_s = set(seg.users(CARNETS, SEANCES_RESTANTES))
c120 = set(seg.users(cree(120)))
cols = sorted({k for u in tous.values() for k in u})
out = [{'id': uid, 'nom': u.get('full_name') or '', 'prenom': u.get('first_name') or '', 'email': (u.get('email') or '').strip().lower(),
        'mobile': u.get('mobile') or '', 'tel': u.get('phone') or '', 'cree_120j': uid in c120, 'a_reserve': uid in venus,
        'reserve_30j': uid in r30, 'abonne_actif': uid in abo, 'carnet_actif': uid in car, 'carnet_seances': uid in car_s,
        'cree_le': u.get('created_at') or u.get('register_date') or ''} for uid, u in tous.items()]
json.dump({'colonnes': cols, 'comptes': out}, open('export.json', 'w'), ensure_ascii=False)
print('comptes exportés', len(out), '| créés sur 120 j', len(c120), '| colonnes disponibles', len(cols))
