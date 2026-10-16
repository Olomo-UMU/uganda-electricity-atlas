#!/usr/bin/env python3
"""Fetch Uganda's high-voltage grid from OpenStreetMap and match it to the atlas model.

Writes data/osm-grid.json with:
  lines   OSM power lines of 66 kV and above (simplified geometry, voltage, name, operator, circuits)
  subs    OSM substations (centre point, voltage, name)
  routes  for each model line id, the route along OSM lines from one substation to the other
  nodes   model substations moved to the matching OSM substation, where the match is clear
  report  what was and was not matched, for checking by hand

Usage:
  python3 tools/osm_grid.py                       # fetch from Overpass, then match
  python3 tools/osm_grid.py --raw overpass.json   # match a saved Overpass response (no download)
Needs only the Python standard library. Run from the electricity-atlas folder (it reads data/lines.csv and data/substations.csv).
"""
import argparse, csv, heapq, json, math, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict

BBOX = (-1.8, 29.3, 4.5, 35.3)  # south, west, north, east: Uganda plus the border substations
ENDPOINTS = ['https://overpass-api.de/api/interpreter',
             'https://overpass.private.coffee/api/interpreter',
             'https://overpass.kumi.systems/api/interpreter']
QUERY = """[out:json][timeout:300];
(way["power"~"^(line|cable)$"]["voltage"~"(66|110|132|220|400)000"]({s},{w},{n},{e}););
out tags geom;
(nwr["power"="substation"]({s},{w},{n},{e}););
out tags center;"""

def fetch():
    q = QUERY.format(s=BBOX[0], w=BBOX[1], n=BBOX[2], e=BBOX[3])
    body = urllib.parse.urlencode({'data': q}).encode()
    last = None
    for attempt in range(3):
        for url in ENDPOINTS:
            try:
                req = urllib.request.Request(url, data=body, headers={'User-Agent': 'uganda-electricity-atlas/1.0 (teaching; GitHub Actions)'})
                with urllib.request.urlopen(req, timeout=360) as r:
                    return json.load(r)
            except Exception as ex:
                last = ex; print(f'  {url}: {ex}', file=sys.stderr)
        time.sleep(30*(attempt + 1))
    raise SystemExit(f'Overpass unavailable: {last}')

def hav(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2 - lon1)/2)**2
    return 12742*math.asin(math.sqrt(h))

def simplify(pts, tol=0.0002):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-12
    im, dm = 0, 0.0
    for i in range(1, len(pts) - 1):
        p = pts[i]; d = abs(dx*(a[1] - p[1]) - dy*(a[0] - p[0]))/L
        if d > dm: im, dm = i, d
    if dm <= tol: return [a, b]
    return simplify(pts[:im + 1], tol)[:-1] + simplify(pts[im:], tol)

def kvs(v):
    out = set()
    for x in str(v or '').split(';'):
        try: out.add(round(float(x)/1000))
        except ValueError: pass
    return out

STOP = {'substation', 'sub', 'station', 'switchyard', 'power', 'kv', 'uetcl', 'uedcl', 'umeme', 'the', 'and', 'planned', 'hpp', 'hydro', 'dam', 'plant', 'ss', 's/s'}
def toks(name):
    return {t for t in re.findall(r'[a-z]+', (name or '').lower()) if t not in STOP and len(t) > 2}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--raw'); ap.add_argument('--out', default='data/osm-grid.json')
    ap.add_argument('--lines', default='data/lines.csv'); ap.add_argument('--subs', default='data/substations.csv')
    a = ap.parse_args()
    raw = json.load(open(a.raw)) if a.raw else fetch()
    els = raw.get('elements', [])
    mlines = list(csv.DictReader(open(a.lines, encoding='utf-8')))
    msubs = {r['id']: r for r in csv.DictReader(open(a.subs, encoding='utf-8'))}

    # ---- OSM lines and the routing graph (vertices shared between ways join them) ----
    ways, subs = [], []
    adj = defaultdict(list); pos = {}
    for e in els:
        t = e.get('tags', {})
        if e['type'] == 'way' and 'geometry' in e and t.get('power') in ('line', 'cable'):
            g = [(round(p['lon'], 6), round(p['lat'], 6)) for p in e['geometry']]
            ids = e.get('nodes') or [f'{x},{y}' for x, y in g]
            ways.append({'id': e['id'], 'v': t.get('voltage', ''), 'n': t.get('name', ''), 'op': t.get('operator', ''), 'ci': t.get('circuits', ''),
                         'g': [[round(x, 5), round(y, 5)] for x, y in simplify(g)]})
            kv = kvs(t.get('voltage'))
            for i in range(len(g) - 1):
                u, v = ids[i], ids[i + 1]; pos[u] = g[i]; pos[v] = g[i + 1]
                d = hav(g[i], g[i + 1]); adj[u].append((v, d, kv, e['id'])); adj[v].append((u, d, kv, e['id']))
        elif t.get('power') == 'substation':
            c = e.get('center') or ({'lat': e['lat'], 'lon': e['lon']} if 'lat' in e else None)
            if c: subs.append({'id': e['type'][0] + str(e['id']), 'v': t.get('voltage', ''), 'n': t.get('name', ''), 'c': [round(c['lon'], 5), round(c['lat'], 5)]})

    # ---- match model substations to OSM substations by name and distance ----
    node_pos, node_rep = {}, []
    for sid, s in msubs.items():
        p = (float(s['lon']), float(s['lat'])); mt = toks(s['name']); best = None
        for o in subs:
            d = hav(p, o['c'])
            if d > 25: continue
            share = len(mt & toks(o['n']))
            score = (share > 0, -d)
            if share and (best is None or score > best[0]): best = (score, o, d)
        if best:
            node_pos[sid] = best[1]['c']; node_rep.append([sid, s['name'], best[1]['n'], round(best[2], 1)])
    # anchor for routing: matched OSM substation, otherwise the model position
    anchor = {sid: tuple(node_pos.get(sid, (float(s['lon']), float(s['lat'])))) for sid, s in msubs.items()}

    # ---- route each model line through the OSM graph ----
    verts = list(pos.items())
    def near(p, r):
        return [(u, hav(p, q)) for u, q in verts if abs(q[0] - p[0]) < r/100 and abs(q[1] - p[1]) < r/100 and hav(p, q) <= r]
    # vertices close to a substation, so a route cannot pass through a third substation on its way
    near_sub = {}
    for u, q in verts:
        for sid, ap in anchor.items():
            if abs(q[0] - ap[0]) < 0.02 and abs(q[1] - ap[1]) < 0.02 and hav(q, ap) < 0.5: near_sub[u] = sid; break
    routes, rep = {}, []
    for l in mlines:
        A, B, kv = l['from_id'], l['to_id'], int(l['voltage_kv'])
        pa, pb = anchor[A], anchor[B]; straight = hav(pa, pb)
        ra = 3 if A in node_pos else 10; rb = 3 if B in node_pos else 10
        src, dst = near(pa, ra), dict(near(pb, rb))
        if not src or not dst: rep.append([l['id'], l['from'], l['to'], kv, 'no OSM line near an end', '']); continue
        dist = {}; prev = {}; pq = []
        for u, d in src: dist[u] = 2*d; heapq.heappush(pq, (2*d, u))
        found = None
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, 1e18): continue
            if u in dst: found = u; break
            if d > 4*straight + 60: break
            for v, w, vk, wid in adj[u]:
                pen = 1.0 if (kv in vk or (kv == 400 and 220 in vk) or (kv == 220 and 400 in vk)) else (1.6 if not vk else 4.0)
                via = near_sub.get(v)
                if via and via not in (A, B): pen += 5
                nd = d + w*pen
                if nd < dist.get(v, 1e18): dist[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
        if not found: rep.append([l['id'], l['from'], l['to'], kv, 'no connected OSM route', '']); continue
        path = [found]
        while path[-1] in prev: path.append(prev[path[-1]])
        path.reverse()
        okv = tot = 0.0
        for u, v in zip(path, path[1:]):
            ed = min((x for x in adj[u] if x[0] == v), key=lambda x: x[1])
            tot += ed[1]
            if kv in ed[2] or (kv == 400 and 220 in ed[2]) or (kv == 220 and 400 in ed[2]): okv += ed[1]
        if tot and okv/tot < 0.7: rep.append([l['id'], l['from'], l['to'], kv, f'route mostly at another voltage ({okv/tot:.0%} at {kv} kV), rejected', round(tot, 1)]); continue
        pts = [pa] + [pos[u] for u in path] + [pb]
        length = sum(hav(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if length > 1.8*straight + 25: rep.append([l['id'], l['from'], l['to'], kv, 'route too long, rejected', round(length, 1)]); continue
        routes[l['id']] = [[round(x, 5), round(y, 5)] for x, y in simplify(pts, 0.0003)]
        rep.append([l['id'], l['from'], l['to'], kv, 'matched', round(length, 1)])

    out = {'ts': raw.get('osm3s', {}).get('timestamp_osm_base', ''), 'bbox': BBOX, 'lines': ways, 'subs': subs,
           'routes': routes, 'nodes': node_pos,
           'report': {'lines': rep, 'substations': node_rep}}
    json.dump(out, open(a.out, 'w'), separators=(',', ':'))
    ok = sum(1 for r in rep if r[4] == 'matched')
    print(f'{len(ways)} OSM lines, {len(subs)} substations; {ok}/{len(mlines)} model lines routed; {len(node_pos)}/{len(msubs)} substations matched -> {a.out}')
    for r in rep:
        if r[4] != 'matched': print('  ', *r)

if __name__ == '__main__':
    main()
