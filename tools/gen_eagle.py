#!/usr/bin/env python3
"""Generate Eagle .lbr / .sch / .brd + BOM for the RTD2660 driver board variants.

usage: python3 tools/gen_eagle.py [output_dir]   (default: ./eagle)
"""
import csv
import math
import os
import sys

from lxml import etree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eaglelib import LAYERS, GRID, f            # noqa: E402
import parts                                    # noqa: E402
import circuit                                  # noqa: E402

EAGLE_VERSION = "7.7.0"
VARIANTS = ("LVDS",)   # RGB40 / RGB50 kept in circuit.py, not generated for now
BOARD_W, BOARD_H = 120.0, 80.0


def snap(v, up=True):
    k = v / GRID
    return (math.ceil(k - 1e-9) if up else math.floor(k + 1e-9)) * GRID


def eagle_root():
    root = etree.Element("eagle", version=EAGLE_VERSION)
    dr = etree.SubElement(root, "drawing")
    st = etree.SubElement(dr, "settings")
    etree.SubElement(st, "setting", alwaysvectorfont="no")
    etree.SubElement(st, "setting", verticaltext="up")
    etree.SubElement(dr, "grid", distance="0.1", unitdist="inch", unit="inch", style="lines",
                     multiple="1", display="no", altdistance="0.01", altunitdist="inch",
                     altunit="inch")
    ly = etree.SubElement(dr, "layers")
    for num, name, color in LAYERS:
        etree.SubElement(ly, "layer", number=str(num), name=name, color=str(color), fill="1",
                         visible="yes", active="yes")
    return root, dr


def write_xml(root, path):
    tree = etree.ElementTree(root)
    with open(path, "wb") as fh:
        fh.write(b'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE eagle SYSTEM "eagle.dtd">\n')
        tree.write(fh, pretty_print=True, encoding="utf-8", xml_declaration=False)


def classes(parent):
    c = etree.SubElement(parent, "classes")
    etree.SubElement(c, "class", number="0", name="default", width="0", drill="0")


# ============================================================================ schematic
LABEL_SIZE = 1.778
STUB = 2 * GRID


def label_len(net):
    return STUB + len(net) * LABEL_SIZE * 0.95 + 1.5


def sch_extent(part):
    """Extent of a placed symbol incl. wire stubs + labels, relative to its origin."""
    sym = part.dev.symbol
    x0, y0, x1, y1 = sym.bbox()
    x0 -= 1; y0 -= 4.5; x1 += 1; y1 += 3.5
    for (name, px, py, _l, rot, _d, _v) in sym.pins:
        net = part.nets.get(name)
        if not net:
            continue
        L = label_len(net)
        if rot == 0:
            x0 = min(x0, px - L)
        elif rot == 180:
            x1 = max(x1, px + L)
        elif rot == 270:
            y1 = max(y1, py + L)
        elif rot == 90:
            y0 = min(y0, py - L)
    return x0, y0, x1, y1


def layout_schematic(d):
    """Shelf-pack groups into blocks and blocks into sheets. Returns sheet sizes and titles."""
    sheet_info = []
    for si, title in enumerate(d.sheets):
        groups = []
        for pn in d.order:
            p = d.parts[pn]
            if p.sheet == si and p.group not in groups:
                groups.append(p.group)
        max_w = 400.0
        cur_x, cur_y, row_h = 0.0, -15.0, 0.0
        titles = []
        for g in groups:
            items = [d.parts[pn] for pn in d.order if d.parts[pn].sheet == si and d.parts[pn].group == g]
            exts = [sch_extent(p) for p in items]
            # block layout: wrap parts in rows of max block width
            bw_max = 200.0 if len(items) > 1 else 1e9
            bx, by, brow, bw, placed = 0.0, 0.0, 0.0, 0.0, []
            for p, (x0, y0, x1, y1) in zip(items, exts):
                w, h = x1 - x0, y1 - y0
                if bx > 0 and bx + w > bw_max:
                    bx, by, brow = 0.0, by - brow - 2.54, 0.0
                placed.append((p, bx - x0, by - y1))   # origin so that cell top-left = (bx, by)
                bx += w + 2.54
                bw = max(bw, bx)
                brow = max(brow, h)
            bh = -(by - brow)
            if cur_x > 0 and cur_x + bw > max_w:
                cur_x, cur_y, row_h = 0.0, cur_y - row_h - 12.0, 0.0
            ox, oy = cur_x, cur_y - 6.0
            titles.append((g, ox, cur_y - 2.5))
            for p, px, py in placed:
                p.sch_xy = (snap(ox + px), snap(oy + py, up=False))
            cur_x += bw + 12.0
            row_h = max(row_h, bh + 8.0)
        bottom = cur_y - row_h
        sheet_info.append((title, titles, bottom))
    return sheet_info


def sch_xml(d, lib):
    info = layout_schematic(d)
    root, dr = eagle_root()
    sch = etree.SubElement(dr, "schematic", xreflabel="%F%N/%S.%C%R", xrefpart="/%S.%C%R")
    etree.SubElement(sch, "description").text = d.title
    libs = etree.SubElement(sch, "libraries")
    libs.append(lib.xml())
    etree.SubElement(sch, "attributes")
    etree.SubElement(sch, "variantdefs")
    classes(sch)
    pe = etree.SubElement(sch, "parts")
    for pn in d.order:
        p = d.parts[pn]
        val = ("DNP " + p.value) if p.dnp else p.value
        etree.SubElement(pe, "part", name=pn, library=lib.name, deviceset=p.dev.name, device="",
                         value=val)
    sheets = etree.SubElement(sch, "sheets")
    for si, (title, gtitles, bottom) in enumerate(info):
        sh = etree.SubElement(sheets, "sheet")
        plain = etree.SubElement(sh, "plain")
        t = etree.SubElement(plain, "text", x="0", y="5.08", size="5.08", layer="97")
        t.text = "%s  -  sheet %d/%d: %s" % (d.title, si + 1, len(info), title)
        for g, x, y in gtitles:
            t = etree.SubElement(plain, "text", x=f(x), y=f(snap(y, up=False)), size="2.54", layer="97")
            t.text = g
        y = bottom - 8
        for line in d.notes.get(si, []):
            t = etree.SubElement(plain, "text", x="0", y=f(snap(y, up=False)), size="2.1844", layer="97")
            t.text = line
            y -= 4.0
        inst = etree.SubElement(sh, "instances")
        nets = {}
        for pn in d.order:
            p = d.parts[pn]
            if p.sheet != si:
                continue
            ix, iy = p.sch_xy
            etree.SubElement(inst, "instance", part=pn, gate="G$1", x=f(ix), y=f(iy))
            sym = p.dev.symbol
            for (name, px, py, _l, rot, _dd, _v) in sym.pins:
                net = p.nets.get(name)
                if not net:
                    continue
                ux, uy = sym.pin_outward(name)
                ax, ay = ix + px, iy + py
                bx, by = ax + ux * STUB, ay + uy * STUB
                lrot = {(-1, 0): "R180", (1, 0): "R0", (0, 1): "R90", (0, -1): "R270"}[(ux, uy)]
                nets.setdefault(net, []).append((pn, name, ax, ay, bx, by, lrot))
        ne = etree.SubElement(sh, "nets")
        for net in sorted(nets):
            n = etree.SubElement(ne, "net", name=net, **{"class": "0"})
            for (pn, pin, ax, ay, bx, by, lrot) in nets[net]:
                seg = etree.SubElement(n, "segment")
                etree.SubElement(seg, "pinref", part=pn, gate="G$1", pin=pin)
                etree.SubElement(seg, "wire", x1=f(ax), y1=f(ay), x2=f(bx), y2=f(by),
                                 width="0.1524", layer="91")
                a = dict(x=f(bx), y=f(by), size=f(LABEL_SIZE), layer="95")
                if lrot != "R0":
                    a["rot"] = lrot
                etree.SubElement(seg, "label", **a)
    return root


# ============================================================================ board
def zones(variant):
    W, H = BOARD_W, BOARD_H
    z = {
        "12V input": [(8, 2, 32, 22)],
        "5V buck": [(30, 2, 82, 22)],
        "LDOs": [(80, 2, W - 7, 25)],
        "Decoupling": [(46, 22, 76, 34.5), (47, 60, 74, 66)],
        "Clock / reset / bias": [(33, 58, 47, 77), (38, 40, 50, 57)],
        "SPI flash": [(47, 66, 76, 77)],
        "Analog front end": [(8, 23, 36, 56)],
        "Sync / DDC": [(8, 56, 33, 70)],
        "Keypad / IR": [(30, 70, 33, 77), (8, 70, 30, 72.5)],
        "VGA 12P header": [],
    }
    out_zone = [(78, 26, W - 9, 70), (76, 70, W - 10, 77)]
    for g in ("LVDS 20P 2.0mm", "Panel power", "Backlight control", "RGB 40P connector",
              "RGB 50P connector", "LED backlight driver", "Panel straps",
              "Panel bias AVDD VGH VGL VCOM"):
        z[g] = out_zone
    return z


FIXED = {
    "U1": (60, 47, 0), "J1": (3.5, 9, 90), "J2": (3.5, 25, 90), "J3": (3.5, 58, 90),
    "J4": (10, 76, 0),
}


def rot_bbox(b, rot):
    x0, y0, x1, y1 = b
    if rot in (90, 270):
        return (-y1, x0, -y0, x1) if rot == 90 else (y0, -x1, y1, -x0)
    if rot == 180:
        return (-x1, -y1, -x0, -y0)
    return b


def place_board(d, variant):
    W, H = BOARD_W, BOARD_H
    fixed = dict(FIXED)
    if variant == "LVDS":
        fixed["J5"] = (W - 3.5, 22, 90)
        fixed["J6"] = (W - 3.5, 64, 90)
    else:
        fixed["J5"] = (W - 3.5, 47, 270)
        if "J6" in d.parts:
            fixed["J6"] = (W - 26, 76, 0)
    holes = [pn for pn in d.order if d.parts[pn].dev.name == "HOLE-M3"]
    for pn, xy in zip(holes, [(3.5, 3.5), (W - 3.5, 3.5), (3.5, H - 3.5), (W - 3.5, H - 3.5)]):
        fixed[pn] = (xy[0], xy[1], 0)
    zs = zones(variant)
    state = {}   # zone rect -> (x, y, row_h)
    overflow = []
    for pn in d.order:
        p = d.parts[pn]
        if pn in fixed:
            x, y, r = fixed[pn]
            p.brd_xy, p.brd_rot = (x, y), r
            continue
        bb = p.dev.package.bbox()
        placed = False
        for rot in (0, 90):
            b = rot_bbox(bb, rot)
            w, h = b[2] - b[0] + 0.8, b[3] - b[1] + 0.8
            for z in zs.get(p.group, []):
                x, y, rh = state.get(z, (z[0], z[1], 0.0))
                if x + w > z[2]:
                    x, y, rh = z[0], y + rh, 0.0
                if y + h <= z[3] and x + w <= z[2]:
                    p.brd_xy = (round(x - b[0] + 0.4, 3), round(y - b[1] + 0.4, 3))
                    p.brd_rot = rot
                    state[z] = (x + w, y, max(rh, h))
                    placed = True
                    break
            if placed:
                break
        if not placed:
            overflow.append(pn)
    # anything that did not fit goes to a parking area right of the board
    x, y = W + 5, 2
    for pn in overflow:
        p = d.parts[pn]
        b = p.dev.package.bbox()
        p.brd_xy, p.brd_rot = (x - b[0], y - b[1]), 0
        y += b[3] - b[1] + 1
        if y > H:
            x, y = x + 15, 2
    return overflow


def brd_xml(d, lib, variant):
    overflow = place_board(d, variant)
    root, dr = eagle_root()
    brd = etree.SubElement(dr, "board")
    plain = etree.SubElement(brd, "plain")
    W, H = BOARD_W, BOARD_H
    for (x1, y1, x2, y2) in ((0, 0, W, 0), (W, 0, W, H), (W, H, 0, H), (0, H, 0, 0)):
        etree.SubElement(plain, "wire", x1=f(x1), y1=f(y1), x2=f(x2), y2=f(y2), width="0",
                         layer="20")
    t = etree.SubElement(plain, "text", x="34", y="56", size="1.27", layer="21")
    t.text = d.title
    used = set(d.parts[pn].dev.package.name for pn in d.order)
    libs = etree.SubElement(brd, "libraries")
    libs.append(lib.xml(with_symbols=False, with_devices=False, only_packages=used))
    etree.SubElement(brd, "attributes")
    etree.SubElement(brd, "variantdefs")
    classes(brd)
    etree.SubElement(brd, "designrules", name="default")
    etree.SubElement(brd, "autorouter")
    els = etree.SubElement(brd, "elements")
    for pn in d.order:
        p = d.parts[pn]
        x, y = p.brd_xy
        val = ("DNP " + p.value) if p.dnp else p.value
        a = dict(name=pn, library=lib.name, package=p.dev.package.name, value=val, x=f(x), y=f(y))
        if p.brd_rot:
            a["rot"] = "R%d" % p.brd_rot
        etree.SubElement(els, "element", **a)
    sigs = etree.SubElement(brd, "signals")
    for net, conns in sorted(d.pad_netlist().items()):
        s = etree.SubElement(sigs, "signal", name=net)
        for (pn, pad) in conns:
            etree.SubElement(s, "contactref", element=pn, pad=pad)
        if net == "GND":
            poly = etree.SubElement(s, "polygon", width="0.3048", layer="16", isolate="0.3048")
            for (x, y) in ((0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)):
                etree.SubElement(poly, "vertex", x=f(x), y=f(y))
    return root, overflow


# ============================================================================ BOM
def write_bom(d, path):
    rows = {}
    for pn in d.order:
        p = d.parts[pn]
        if p.dev.name == "HOLE-M3":
            continue
        key = (p.value, p.dev.package.name, p.dev.description, p.dnp)
        rows.setdefault(key, []).append(pn)

    def natkey(n):
        import re
        m = re.match(r"([A-Z]+)(\d+)", n)
        return (m.group(1), int(m.group(2))) if m else (n, 0)

    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Qty", "Value", "Package", "Description", "Fit", "References"])
        for (val, pkg, desc, dnp), refs in sorted(rows.items(), key=lambda kv: natkey(sorted(kv[1], key=natkey)[0])):
            refs = sorted(refs, key=natkey)
            w.writerow([len(refs), val, pkg, desc, "DNP" if dnp else "yes", " ".join(refs)])


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eagle")
    os.makedirs(out, exist_ok=True)
    lib = parts.build_library()
    # library file
    root, dr = eagle_root()
    lw = etree.SubElement(dr, "library")
    full = lib.xml()
    for child in full:
        lw.append(child)
    write_xml(root, os.path.join(out, "%s.lbr" % lib.name))
    for v in VARIANTS:
        d = circuit.build(v, lib)
        base = os.path.join(out, "RTD2660_VGA12P_%s" % v)
        write_xml(sch_xml(d, lib), base + ".sch")
        broot, overflow = brd_xml(d, lib, v)
        write_xml(broot, base + ".brd")
        write_bom(d, base + "_BOM.csv")
        print("%-6s %3d parts %3d nets -> %s.sch/.brd%s" % (
            v, len(d.parts), len(d.netlist()), base,
            ("  (not placed on board: %s)" % " ".join(overflow)) if overflow else ""))


if __name__ == "__main__":
    main()
