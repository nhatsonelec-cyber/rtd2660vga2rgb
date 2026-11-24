#!/usr/bin/env python3
"""Render PDF previews (schematic sheets + board placement) of the generated designs.

usage: python3 tools/preview.py [output_dir]   (needs matplotlib)
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                       # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Rectangle, Circle, Polygon  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_eagle as G     # noqa: E402
import parts, circuit     # noqa: E402


def tr(x, y, rot):
    r = math.radians(rot)
    return x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)


def draw_board(ax, d):
    W, H = G.BOARD_W, G.BOARD_H
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=1.2, ec="k"))
    for pn in d.order:
        p = d.parts[pn]
        pk = p.dev.package
        X, Y = p.brd_xy
        rot = p.brd_rot
        for (name, x, y, dx, dy, r, _rn, _c) in pk.smds:
            if (r + rot) % 180 == 90:
                dx, dy = dy, dx
            cx, cy = tr(x, y, rot)
            ax.add_patch(Rectangle((X + cx - dx / 2, Y + cy - dy / 2), dx, dy, color="#c83737", lw=0))
        for (name, x, y, drill, dia, shape) in pk.pads:
            cx, cy = tr(x, y, rot)
            ax.add_patch(Circle((X + cx, Y + cy), dia / 2, color="#b8860b", lw=0))
            ax.add_patch(Circle((X + cx, Y + cy), drill / 2, color="w", lw=0))
        for (x, y, dr) in pk.holes:
            cx, cy = tr(x, y, rot)
            ax.add_patch(Circle((X + cx, Y + cy), dr / 2, fill=False, ec="k", lw=0.8))
        for (x1, y1, x2, y2, w, layer) in pk.wires:
            a = tr(x1, y1, rot); b = tr(x2, y2, rot)
            ax.plot([X + a[0], X + b[0]], [Y + a[1], Y + b[1]],
                    color="#1f5fbf" if layer == 21 else "#999", lw=0.4)
        for (x, y, r, w, layer) in pk.circles:
            cx, cy = tr(x, y, rot)
            ax.add_patch(Circle((X + cx, Y + cy), r, fill=False, ec="#1f5fbf", lw=0.4))
        b = G.rot_bbox(pk.bbox(), rot)
        fs = 4.5 if pn.startswith(("U", "J")) else 2.6
        ax.text(X + (b[0] + b[2]) / 2, Y + (b[1] + b[3]) / 2, pn, fontsize=fs, ha="center",
                va="center", color="k")
    ax.set_xlim(-2, W + 2); ax.set_ylim(-2, H + 2)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(d.title + "  -  board %dx%d mm, parts placed, NOT routed" % (W, H), fontsize=9)


def draw_sheet(ax, d, si, info):
    title, gtitles, bottom = info
    xs, ys = [0], [0, bottom - 8 - 4 * len(d.notes.get(si, []))]
    for pn in d.order:
        p = d.parts[pn]
        if p.sheet != si:
            continue
        sym = p.dev.symbol
        X, Y = p.sch_xy
        for (x1, y1, x2, y2, w, l) in sym.wires:
            ax.plot([X + x1, X + x2], [Y + y1, Y + y2], color="#8b0000", lw=0.5)
        for pts in sym.polys:
            ax.add_patch(Polygon([(X + a, Y + b) for a, b in pts], closed=True, color="#8b0000"))
        for (x, y, r, w) in sym.circles:
            ax.add_patch(Circle((X + x, Y + y), r, fill=False, ec="#8b0000", lw=0.5))
        for (name, px, py, length, rot, _d, _v) in sym.pins:
            L = {"point": 0, "short": 2.54, "middle": 5.08, "long": 7.62}[length]
            dx, dy = {0: (1, 0), 180: (-1, 0), 90: (0, 1), 270: (0, -1)}[rot]
            ax.plot([X + px, X + px + dx * L], [Y + py, Y + py + dy * L], color="#8b0000", lw=0.4)
            if p.dev.symbol.name not in ("R", "C", "CP", "L", "D", "Z", "LED", "F", "XTAL"):
                shown = name.split("@")[0]
                ix, iy = X + px + dx * (L + 0.6), Y + py + dy * (L + 0.6)
                ha = "left" if dx > 0 else "right" if dx < 0 else "center"
                ax.text(ix, iy, shown, fontsize=2.4, ha=ha, va="center",
                        rotation=90 if dy else 0, color="#333")
            net = p.nets.get(name)
            if net:
                ux, uy = -dx, -dy
                bx, by = X + px + ux * G.STUB, Y + py + uy * G.STUB
                ax.plot([X + px, bx], [Y + py, by], color="#006400", lw=0.4)
                ha = "left" if ux > 0 else "right" if ux < 0 else "center"
                va = "center" if ux else ("bottom" if uy > 0 else "top")
                ax.text(bx + ux * 0.5, by + uy * 0.5, net, fontsize=2.4, ha=ha, va=va,
                        rotation=90 if uy else 0, color="#006400")
        bx0, by0, bx1, by1 = sym.bbox()
        val = ("DNP " + p.value) if p.dnp else p.value
        ax.text(X + bx0, Y + by1 + 0.8, pn, fontsize=3.0, color="k", weight="bold")
        ax.text(X + bx0, Y + by0 - 0.8, val, fontsize=2.6, color="#444", va="top")
        e = G.sch_extent(p)
        xs += [X + e[0], X + e[2]]; ys += [Y + e[1], Y + e[3]]
    for g, x, y in gtitles:
        ax.text(x, y, g, fontsize=4.5, color="#1f3f7f", weight="bold")
    y = bottom - 8
    for line in d.notes.get(si, []):
        ax.text(0, y, line, fontsize=4, color="#1f3f7f")
        y -= 4
    ax.set_xlim(min(xs) - 5, max(xs) + 5); ax.set_ylim(min(ys) - 5, max(ys) + 8)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("%s  -  sheet %d/%d: %s" % (d.title, si + 1, len(d.sheets), title), fontsize=8)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "preview")
    os.makedirs(out, exist_ok=True)
    lib = parts.build_library()
    for v in G.VARIANTS:
        d = circuit.build(v, lib)
        info = G.layout_schematic(d)
        G.place_board(d, v)
        path = os.path.join(out, "RTD2660_VGA12P_%s_preview.pdf" % v)
        with PdfPages(path) as pdf:
            for si in range(len(d.sheets)):
                fig = plt.figure(figsize=(16.5, 11.7))
                ax = fig.add_axes([0.01, 0.01, 0.98, 0.95])
                draw_sheet(ax, d, si, info[si])
                pdf.savefig(fig); plt.close(fig)
            fig = plt.figure(figsize=(16.5, 11.7))
            ax = fig.add_axes([0.02, 0.02, 0.96, 0.93])
            draw_board(ax, d)
            pdf.savefig(fig); plt.close(fig)
        print(path)


if __name__ == "__main__":
    main()
