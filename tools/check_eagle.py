#!/usr/bin/env python3
"""Independent consistency check of generated Eagle files (re-reads the XML only).

- every schematic pinref points to an existing part / gate / symbol pin
- every net wire starts exactly on its pin connection point, labels sit on wires
- every device connect maps to an existing pad
- schematic netlist (via device connects) == board signals (element/pad)
"""
import glob, os, sys
from lxml import etree


def check(sch_path, brd_path):
    errs = []
    s = etree.parse(sch_path).getroot()
    lib = s.find(".//schematic/libraries/library")
    syms = {e.get("name"): {p.get("name"): (float(p.get("x")), float(p.get("y")))
                             for p in e.findall("pin")} for e in lib.findall("symbols/symbol")}
    pkgs = {e.get("name"): set(x.get("name") for x in e.findall("smd") + e.findall("pad"))
            for e in lib.findall("packages/package")}
    devs = {}
    for ds in lib.findall("devicesets/deviceset"):
        gate = ds.find("gates/gate")
        dev = ds.find("devices/device")
        con = {c.get("pin"): c.get("pad") for c in dev.findall("connects/connect")}
        pk = dev.get("package")
        for pin, pad in con.items():
            if pad not in pkgs.get(pk, ()):
                errs.append("deviceset %s: pad %s missing" % (ds.get("name"), pad))
            if pin not in syms[gate.get("symbol")]:
                errs.append("deviceset %s: pin %s missing" % (ds.get("name"), pin))
        devs[ds.get("name")] = (gate.get("symbol"), pk, con)
    parts = {p.get("name"): p.get("deviceset") for p in s.findall(".//parts/part")}
    sch_nets = {}
    for sheet in s.findall(".//sheets/sheet"):
        inst = {i.get("part"): (float(i.get("x")), float(i.get("y"))) for i in sheet.findall("instances/instance")}
        for net in sheet.findall("nets/net"):
            for seg in net.findall("segment"):
                pr = seg.find("pinref"); w = seg.find("wire"); lb = seg.find("label")
                part, pin = pr.get("part"), pr.get("pin")
                if part not in parts or part not in inst:
                    errs.append("pinref to unknown/uninstanced part %s" % part); continue
                sym, pk, con = devs[parts[part]]
                if pin not in syms[sym]:
                    errs.append("%s has no pin %s" % (part, pin)); continue
                px = inst[part][0] + syms[sym][pin][0]; py = inst[part][1] + syms[sym][pin][1]
                if abs(float(w.get("x1")) - px) > 1e-3 or abs(float(w.get("y1")) - py) > 1e-3:
                    errs.append("wire not on pin %s.%s" % (part, pin))
                if abs(float(lb.get("x")) - float(w.get("x2"))) > 1e-3 or abs(float(lb.get("y")) - float(w.get("y2"))) > 1e-3:
                    errs.append("label off wire %s" % net.get("name"))
                if abs(px / 2.54 - round(px / 2.54)) > 1e-3 or abs(py / 2.54 - round(py / 2.54)) > 1e-3:
                    errs.append("pin off 0.1in grid %s.%s" % (part, pin))
                sch_nets.setdefault(net.get("name"), set()).add((part, con[pin]))
    b = etree.parse(brd_path).getroot()
    bpk = {e.get("name"): set(x.get("name") for x in e.findall("smd") + e.findall("pad"))
           for e in b.findall(".//board/libraries/library/packages/package")}
    els = {e.get("name"): e.get("package") for e in b.findall(".//elements/element")}
    if set(els) != set(parts):
        errs.append("part/element mismatch: %s" % (set(els) ^ set(parts)))
    for name, ds in parts.items():
        if devs[ds][1] != els.get(name):
            errs.append("package mismatch %s" % name)
    brd_nets = {}
    for sig in b.findall(".//signals/signal"):
        for c in sig.findall("contactref"):
            if c.get("pad") not in bpk[els[c.get("element")]]:
                errs.append("contactref to missing pad %s.%s" % (c.get("element"), c.get("pad")))
            brd_nets.setdefault(sig.get("name"), set()).add((c.get("element"), c.get("pad")))
    if sch_nets != brd_nets:
        errs.append("netlist differs: %s" % sorted(set(sch_nets) ^ set(brd_nets))[:10])
        for n in set(sch_nets) & set(brd_nets):
            if sch_nets[n] != brd_nets[n]:
                errs.append("net %s differs" % n)
    return errs, len(parts), len(sch_nets)


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "eagle"
    bad = 0
    for sch in sorted(glob.glob(os.path.join(d, "*.sch"))):
        errs, np, nn = check(sch, sch[:-4] + ".brd")
        print("%-34s parts %3d nets %3d  %s" % (os.path.basename(sch), np, nn, "OK" if not errs else "ERRORS"))
        for e in errs[:20]:
            print("   ", e)
        bad += len(errs)
    sys.exit(1 if bad else 0)
