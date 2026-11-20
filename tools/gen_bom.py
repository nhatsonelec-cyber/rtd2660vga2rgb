"""Write docs/bom.csv grouped by value + footprint."""
import os, sys, csv, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import d
from placement import P
rows = {}
for c in d.comps:
    if c.sym == 'Mechanical:MountingHole': continue
    key = (c.value, c.fp.split(':')[1], 'DNP' if c.dnp else '')
    rows.setdefault(key, []).append(c.ref)
def nat(r): m = re.match(r'([A-Z]+)(\d+)', r); return (m.group(1), int(m.group(2)))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'bom.csv')
with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Qty', 'References', 'Value', 'Footprint', 'Side', 'Note'])
    for (val, fp, dnp), refs in sorted(rows.items(), key=lambda kv: nat(sorted(kv[1], key=nat)[0])):
        refs = sorted(refs, key=nat)
        sides = sorted(set('top' if P[r][3] == 'F' else 'bottom' for r in refs))
        w.writerow([len(refs), ' '.join(refs), val, fp, '/'.join(sides), dnp])
print('bom lines:', len(rows), 'parts:', sum(len(v) for v in rows.values()))
