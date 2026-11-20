"""Export the netlist from the generated schematic with kicad-cli and compare it
with the netlist defined in design.py (pin-for-pin)."""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, find, first
HW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hardware')
out = os.path.join(tempfile.gettempdir(), 'rtd_check.net')
r = subprocess.run(['kicad-cli', 'sch', 'export', 'netlist', '-o', out, os.path.join(HW, 'rtd2660vga2rgb.kicad_sch')],
                   capture_output=True, text=True)
print(r.stdout.strip()[-300:], r.stderr.strip()[-300:])
t = parse(open(out).read())
got = {}
for n in find(first(t, 'nets'), 'net'):
    name = first(n, 'name')[1].lstrip('/')
    got[name] = sorted((first(x, 'ref')[1], first(x, 'pin')[1]) for x in find(n, 'node'))
exp = {k: [tuple(x) for x in v] for k, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netlist_expected.json'))).items()}
# pins -> net maps
def pinmap(nl):
    return {p: n for n, v in nl.items() for p in v}
pg, pe = pinmap(got), pinmap(exp)
bad = 0
for p, n in sorted(pe.items()):
    if pg.get(p) != n:
        bad += 1
        if bad < 40: print('MISMATCH', p, 'expected', n, 'got', pg.get(p))
for p, n in sorted(pg.items()):
    if p not in pe and not n.startswith('unconnected-'):
        bad += 1
        if bad < 40: print('EXTRA', p, n)
comps = find(first(t, 'components'), 'comp')
print('components in netlist:', len(comps), 'nets expected:', len(exp), 'nets exported (named):',
      len([n for n in got if not n.startswith('unconnected-')]), 'mismatches:', bad)
sys.exit(1 if bad else 0)
