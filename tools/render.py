"""Render the PCB (top and bottom views) to PNG for visual inspection."""
import os, sys, subprocess
HW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hardware')
out = sys.argv[1]
scale = sys.argv[2] if len(sys.argv) > 2 else '14'
os.makedirs(out, exist_ok=True)
pcb = os.path.join(HW, 'rtd2660vga2rgb.kicad_pcb')
views = {'top': 'F.Cu,F.SilkS,F.Fab,F.CrtYd,Edge.Cuts', 'bot': 'B.Cu,B.SilkS,B.Fab,B.CrtYd,Edge.Cuts',
         'in1': 'In1.Cu,Edge.Cuts', 'in2': 'In2.Cu,Edge.Cuts', 'cu': 'F.Cu,B.Cu,Edge.Cuts'}
want = sys.argv[3].split(',') if len(sys.argv) > 3 else ['top', 'bot']
for name in want:
    svg = os.path.join(out, name + '.svg')
    cmd = ['kicad-cli', 'pcb', 'export', 'svg', '-o', svg, '-l', views[name], '--page-size-mode', '2', '--exclude-drawing-sheet']
    if name == 'bot': cmd.append('--mirror')
    r = subprocess.run(cmd + [pcb], capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr)
js = r"""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); 
  for (const n of process.argv[3].split(',')) {
    const p = await b.newPage({deviceScaleFactor: 1});
    const svg = require('fs').readFileSync(process.argv[2] + '/' + n + '.svg', 'utf8');
    await p.setContent('<html><body style="margin:0;background:#fff">' + svg + '</body></html>');
    const el = await p.$('svg');
    const s = parseFloat(process.argv[4]);
    await p.evaluate((s) => { const e = document.querySelector('svg'); const vb = e.viewBox.baseVal; e.setAttribute('width', vb.width * s); e.setAttribute('height', vb.height * s); }, s);
    const bb = await el.boundingBox();
    await p.setViewportSize({width: Math.ceil(bb.width), height: Math.ceil(bb.height)});
    await el.screenshot({path: process.argv[2] + '/' + n + '.png'});
  }
  await b.close();
})();
"""
open(os.path.join(out, 'shot.js'), 'w').write(js)
r = subprocess.run(['node', os.path.join(out, 'shot.js'), out, ','.join(want), scale], capture_output=True, text=True, cwd='/tmp')
print(r.stdout[-300:], r.stderr[-600:])
