"""Exploration ResaWod (journal public : n'affiche que des chemins, des noms de champs et des nombres)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brief import ResaWod, RESAWOD

r = ResaWod(os.environ['RESAWOD_USER'], os.environ['RESAWOD_PASSWORD'])

def page(chemin):
    try:
        return r.op.open(RESAWOD + chemin, timeout=30).read().decode('utf-8', 'ignore')
    except Exception as e:
        return 'ERR %s' % e

def structure(x, prof=0):
    if isinstance(x, dict):
        return {k: structure(v, prof + 1) if prof < 3 else type(v).__name__ for k, v in list(x.items())[:60]}
    if isinstance(x, list):
        return ['%d éléments' % len(x)] + ([structure(x[0], prof + 1)] if x else [])
    return type(x).__name__

for chemin in (os.environ.get('PAGES') or '/module/users,/modules/users/').split(','):
    h = page(chemin)
    print('\n=== PAGE', chemin, len(h))
    for motif in (r'/api/v\d/[A-Za-z0-9_/.\-{}$]+', r'[A-Za-z0-9_/\-]*ajax/[A-Za-z0-9_/\-]+\.php', r'/public/react/build/assets/js/[A-Za-z0-9_\-]+\.js'):
        print(sorted(set(re.findall(motif, h)))[:80])

for js in (os.environ.get('JS') or '').split(','):
    if not js:
        continue
    t = page(js)
    print('\n=== JS', js, len(t))
    print(sorted(set(m for m in re.findall(r'["`]([a-z][a-z0-9_\-]*(?:/[a-z0-9_\-${}.]+)+)["`]', t) if 'user' in m or 'member' in m or 'booking' in m or 'attend' in m or 'access' in m))[:150])

for appel in (os.environ.get('APPELS') or '').split(';'):
    if not appel:
        continue
    chemin, _, params = appel.partition('?')
    p = dict(x.split('=', 1) for x in params.split('&') if '=' in x)
    try:
        d = r.get(chemin, **p)
        print('\n=== APPEL', appel)
        print(json.dumps(structure(d), ensure_ascii=False)[:3000])
    except Exception as e:
        print('\n=== APPEL', appel, 'ERR', str(e)[:200])
