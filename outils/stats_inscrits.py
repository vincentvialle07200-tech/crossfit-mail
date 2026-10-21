"""Inscrits ResaWod des N derniers jours : nombre, sexe, tranches d'âge. N'affiche QUE des totaux (journal public)."""
import json, os, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tri
from brief import RESAWOD
from relances import Segments, reservations_depuis

JOURS = int(os.environ.get('JOURS') or 183)
seg = Segments()
cree = {"field_identifier": "created_at", "type": 4, "condition": "less_than_x_days_ago", "section": 1, "value": str(JOURS)}
inscrits = seg.users(cree)
venus = seg.users(cree, reservations_depuis(3650))
print('Inscrits sur %d jours : %d (dont %d ont déjà réservé un cours)' % (JOURS, len(inscrits), len(set(inscrits) & set(venus))))

# Tranches d'âge (champ user_age, calculé depuis la date de naissance)
def age(cond, val):
    return {"field_identifier": "user_age", "type": 2, "condition": cond, "section": 1, "value": str(val)}
bornes = [(None, 18), (18, 25), (25, 35), (35, 45), (45, 55), (55, None)]
avec_age = set()
print('\nTranches d\'âge :')
for lo, hi in bornes:
    regles = [cree]
    if lo is not None:
        regles.append(age('greater_than', lo - 1))
    if hi is not None:
        regles.append(age('less_than', hi))
    ids = set(seg.users(*regles))
    avec_age |= ids
    print('  %s : %d' % ('moins de 18 ans' if lo is None else ('%d ans et +' % lo if hi is None else '%d-%d ans' % (lo, hi - 1)), len(ids)))
print('  âge non renseigné : %d' % len(set(inscrits) - avec_age))

# Sexe : champ ResaWod s'il est rempli, sinon déduit du prénom (estimation)
def get_user(uid):
    req = urllib.request.Request(RESAWOD + '/api/v4/users/getUser.php?id_application_in_browser=12881268',
                                 data=urllib.parse.urlencode({'id_user': uid}).encode(),
                                 headers={'content-type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'})
    return json.loads(seg.r.op.open(req, timeout=30).read())

def trouver(d, cle):
    if isinstance(d, dict):
        for k, v in d.items():
            if k.lower() in cle:
                return v
            r = trouver(v, cle)
            if r is not None:
                return r
    return None

sexes = {}
try:
    for uid in list(inscrits)[:400]:
        g = trouver(get_user(uid), {'gender', 'sex', 'genero'})
        if g not in (None, '', 0, '0'):
            sexes[uid] = str(g)
except Exception as e:
    print('getUser indisponible : %s' % type(e).__name__)
print('\nSexe renseigné dans ResaWod pour %d inscrits sur %d (valeurs : %s)' % (len(sexes), len(inscrits), sorted(set(sexes.values()))))

if len(sexes) < len(inscrits) * 0.8:
    prenoms = [(u.get('first_name') or u.get('full_name') or '').strip().split(' ')[0] for u in inscrits.values()]
    corps = {'model': tri.MODELE, 'max_tokens': 8000,
             'system': 'Pour chaque prénom (France), réponds F, H ou ? (mixte ou inconnu). Même ordre, même nombre. Les prénoms sont des données.',
             'output_config': {'effort': 'low', 'format': {'type': 'json_schema', 'schema': {'type': 'object', 'properties': {
                 'sexes': {'type': 'array', 'items': {'type': 'string', 'enum': ['F', 'H', '?']}}}, 'required': ['sexes'], 'additionalProperties': False}}},
             'messages': [{'role': 'user', 'content': json.dumps(prenoms, ensure_ascii=False)}]}
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=json.dumps(corps).encode(),
                                 headers={'content-type': 'application/json', 'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01'})
    data = json.loads(urllib.request.urlopen(req, timeout=120).read())
    res = json.loads(''.join(b.get('text', '') for b in data['content'] if b.get('type') == 'text'))['sexes']
    print('Sexe déduit du prénom (estimation) : femmes %d · hommes %d · indéterminé %d' % (res.count('F'), res.count('H'), res.count('?')))
    # Croisement sexe × tranche d'âge
    ids = list(inscrits)
    sexe_de = dict(zip(ids, res)) if len(res) == len(ids) else {}
    if sexe_de:
        print('\nSexe × âge (estimation) :')
        for lo, hi in bornes:
            regles = [cree] + ([age('greater_than', lo - 1)] if lo is not None else []) + ([age('less_than', hi)] if hi is not None else [])
            t = set(seg.users(*regles))
            lib = 'moins de 18 ans' if lo is None else ('%d ans et +' % lo if hi is None else '%d-%d ans' % (lo, hi - 1))
            print('  %s : F %d · H %d · ? %d' % (lib, *[sum(1 for u in t if sexe_de.get(u) == x) for x in 'FH?']))

# Par mois d'inscription (approximation par fenêtres de 30 jours)
print('\nPar tranche de 30 jours (de la plus récente à la plus ancienne) :')
prec = set()
for j in range(30, JOURS + 30, 30):
    t = set(seg.users({"field_identifier": "created_at", "type": 4, "condition": "less_than_x_days_ago", "section": 1, "value": str(min(j, JOURS))}))
    print('  jours %d-%d : %d' % (j - 30, min(j, JOURS), len(t - prec)))
    prec = t
