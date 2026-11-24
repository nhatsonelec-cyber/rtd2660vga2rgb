"""Minimal Eagle XML writer: library model, schematic and board output.

Everything (symbols, packages, devices, parts, nets) is described in Python and
written as Eagle 7.x XML (.lbr / .sch / .brd), which Eagle 7, 8 and 9 open.
"""
import math
from lxml import etree

GRID = 2.54

LAYERS = [
    (1, "Top", 4), (2, "Route2", 1), (3, "Route3", 4), (14, "Route14", 1), (15, "Route15", 4),
    (16, "Bottom", 1), (17, "Pads", 2), (18, "Vias", 2), (19, "Unrouted", 6), (20, "Dimension", 15),
    (21, "tPlace", 7), (22, "bPlace", 7), (23, "tOrigins", 15), (24, "bOrigins", 15), (25, "tNames", 7),
    (26, "bNames", 7), (27, "tValues", 7), (28, "bValues", 7), (29, "tStop", 7), (30, "bStop", 7),
    (31, "tCream", 7), (32, "bCream", 7), (33, "tFinish", 6), (34, "bFinish", 6), (35, "tGlue", 7),
    (36, "bGlue", 7), (37, "tTest", 7), (38, "bTest", 7), (39, "tKeepout", 4), (40, "bKeepout", 1),
    (41, "tRestrict", 4), (42, "bRestrict", 1), (43, "vRestrict", 2), (44, "Drills", 7), (45, "Holes", 7),
    (46, "Milling", 3), (47, "Measures", 7), (48, "Document", 7), (49, "Reference", 7), (51, "tDocu", 7),
    (52, "bDocu", 7), (90, "Modules", 5), (91, "Nets", 2), (92, "Busses", 1), (93, "Pins", 2),
    (94, "Symbols", 4), (95, "Names", 7), (96, "Values", 7), (97, "Info", 7), (98, "Guide", 6),
]


def f(v):
    """Format a coordinate the way Eagle does (no trailing zeros)."""
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ----------------------------------------------------------------------------- packages
class Package:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.smds = []    # name, x, y, dx, dy, rot, roundness, cream
        self.pads = []    # name, x, y, drill, diameter, shape
        self.holes = []   # x, y, drill
        self.wires = []   # x1, y1, x2, y2, width, layer
        self.circles = [] # x, y, r, width, layer
        self.rects = []   # x1, y1, x2, y2, layer
        self.texts = []   # text, x, y, size, layer

    def smd(self, name, x, y, dx, dy, rot=0, roundness=0, cream=True):
        self.smds.append((str(name), x, y, dx, dy, rot, roundness, cream))

    def pad(self, name, x, y, drill, dia, shape="round"):
        self.pads.append((str(name), x, y, drill, dia, shape))

    def hole(self, x, y, drill):
        self.holes.append((x, y, drill))

    def wire(self, x1, y1, x2, y2, w=0.2, layer=21):
        self.wires.append((x1, y1, x2, y2, w, layer))

    def rect_outline(self, x1, y1, x2, y2, w=0.2, layer=21):
        self.wire(x1, y1, x2, y1, w, layer); self.wire(x2, y1, x2, y2, w, layer)
        self.wire(x2, y2, x1, y2, w, layer); self.wire(x1, y2, x1, y1, w, layer)

    def circle(self, x, y, r, w=0.2, layer=21):
        self.circles.append((x, y, r, w, layer))

    def names(self, x, y, size=1.0):
        self.texts.append((">NAME", x, y, size, 25))
        self.texts.append((">VALUE", x, y - size * 1.5, size, 27))

    def pad_names(self):
        return [s[0] for s in self.smds] + [p[0] for p in self.pads]

    def bbox(self):
        xs, ys = [], []
        for (_, x, y, dx, dy, rot, _, _) in self.smds:
            if rot in (90, 270):
                dx, dy = dy, dx
            xs += [x - dx / 2, x + dx / 2]; ys += [y - dy / 2, y + dy / 2]
        for (_, x, y, _, d, _) in self.pads:
            xs += [x - d / 2, x + d / 2]; ys += [y - d / 2, y + d / 2]
        for (x, y, d) in self.holes:
            xs += [x - d / 2, x + d / 2]; ys += [y - d / 2, y + d / 2]
        for (x1, y1, x2, y2, w, layer) in self.wires:
            if layer in (21, 51):
                xs += [x1, x2]; ys += [y1, y2]
        for (x, y, r, w, layer) in self.circles:
            xs += [x - r, x + r]; ys += [y - r, y + r]
        if not xs:
            return (-1, -1, 1, 1)
        return (min(xs), min(ys), max(xs), max(ys))

    def xml(self):
        e = etree.Element("package", name=self.name)
        etree.SubElement(e, "description").text = self.description
        for (x1, y1, x2, y2, w, layer) in self.wires:
            etree.SubElement(e, "wire", x1=f(x1), y1=f(y1), x2=f(x2), y2=f(y2), width=f(w), layer=str(layer))
        for (x, y, r, w, layer) in self.circles:
            etree.SubElement(e, "circle", x=f(x), y=f(y), radius=f(r), width=f(w), layer=str(layer))
        for (x1, y1, x2, y2, layer) in self.rects:
            etree.SubElement(e, "rectangle", x1=f(x1), y1=f(y1), x2=f(x2), y2=f(y2), layer=str(layer))
        for (name, x, y, dx, dy, rot, rnd, cream) in self.smds:
            a = dict(name=name, x=f(x), y=f(y), dx=f(dx), dy=f(dy), layer="1")
            if rnd:
                a["roundness"] = str(rnd)
            if rot:
                a["rot"] = "R%d" % rot
            if not cream:
                a["cream"] = "no"
            etree.SubElement(e, "smd", **a)
        for (name, x, y, drill, dia, shape) in self.pads:
            etree.SubElement(e, "pad", name=name, x=f(x), y=f(y), drill=f(drill), diameter=f(dia), shape=shape)
        for (x, y, d) in self.holes:
            etree.SubElement(e, "hole", x=f(x), y=f(y), drill=f(d))
        for (t, x, y, s, layer) in self.texts:
            el = etree.SubElement(e, "text", x=f(x), y=f(y), size=f(s), layer=str(layer))
            el.text = t
        return e


# ----------------------------------------------------------------------------- symbols
class Symbol:
    """Pins: (name, x, y, length, rot, direction). Connection point is (x, y)."""
    LEN = {"point": 0, "short": 2.54, "middle": 5.08, "long": 7.62}

    def __init__(self, name):
        self.name = name
        self.pins = []
        self.wires = []
        self.texts = []
        self.circles = []
        self.polys = []

    def pin(self, name, x, y, length="short", rot=0, direction="pas", visible="pin"):
        self.pins.append((name, x, y, length, rot, direction, visible))

    def wire(self, x1, y1, x2, y2, w=0.254, layer=94):
        self.wires.append((x1, y1, x2, y2, w, layer))

    def rect(self, x1, y1, x2, y2, w=0.254):
        self.wire(x1, y1, x2, y1, w); self.wire(x2, y1, x2, y2, w)
        self.wire(x2, y2, x1, y2, w); self.wire(x1, y2, x1, y1, w)

    def text(self, t, x, y, size=1.778, layer=95):
        self.texts.append((t, x, y, size, layer))

    def pin_point(self, name):
        for p in self.pins:
            if p[0] == name:
                return p[1], p[2]
        raise KeyError("%s has no pin %s" % (self.name, name))

    def pin_outward(self, name):
        """Unit vector pointing away from the symbol body at the pin connection point."""
        for p in self.pins:
            if p[0] == name:
                rot = p[4]
                return {0: (-1, 0), 180: (1, 0), 90: (0, -1), 270: (0, 1)}[rot]
        raise KeyError(name)

    def bbox(self):
        xs, ys = [], []
        for (x1, y1, x2, y2, w, l) in self.wires:
            xs += [x1, x2]; ys += [y1, y2]
        for p in self.pins:
            xs.append(p[1]); ys.append(p[2])
        for (x, y, r, w) in self.circles:
            xs += [x - r, x + r]; ys += [y - r, y + r]
        return (min(xs), min(ys), max(xs), max(ys))

    def xml(self):
        e = etree.Element("symbol", name=self.name)
        for (x1, y1, x2, y2, w, layer) in self.wires:
            etree.SubElement(e, "wire", x1=f(x1), y1=f(y1), x2=f(x2), y2=f(y2), width=f(w), layer=str(layer))
        for (x, y, r, w) in self.circles:
            etree.SubElement(e, "circle", x=f(x), y=f(y), radius=f(r), width=f(w), layer="94")
        for pts in self.polys:
            pe = etree.SubElement(e, "polygon", width="0.254", layer="94")
            for (x, y) in pts:
                etree.SubElement(pe, "vertex", x=f(x), y=f(y))
        for (t, x, y, s, layer) in self.texts:
            el = etree.SubElement(e, "text", x=f(x), y=f(y), size=f(s), layer=str(layer))
            el.text = t
        for (name, x, y, length, rot, direction, visible) in self.pins:
            a = dict(name=name, x=f(x), y=f(y), length=length, direction=direction, visible=visible)
            if rot:
                a["rot"] = "R%d" % rot
            etree.SubElement(e, "pin", **a)
        return e


def box_symbol(name, left, right, width=None, top=None, bottom=None, pin_len="middle"):
    """Rectangular IC symbol. left/right: lists of pin names (None = gap)."""
    top = top or []
    bottom = bottom or []
    s = Symbol(name)
    L = Symbol.LEN[pin_len]
    rows = max(len(left), len(right), 1)
    if width is None:
        longest = max([len(p) for p in left + right if p] + [4])
        width = max(15.24, math.ceil((longest * 1.778 * 0.85 * 2 + 5.08) / 5.08) * 5.08)
        width = max(width, math.ceil((len(top) * 2.54 + 5.08) / 5.08) * 5.08)
        width = max(width, math.ceil((len(bottom) * 2.54 + 5.08) / 5.08) * 5.08)
    width = math.ceil(width / (2 * GRID) - 1e-9) * 2 * GRID   # keep pins on the 0.1 in grid
    hw = width / 2
    y_top = GRID
    y_bot = -rows * GRID
    s.rect(-hw, y_bot, hw, y_top)
    for i, p in enumerate(left):
        if p:
            s.pin(p, -hw - L, -i * GRID, pin_len, 0)
    for i, p in enumerate(right):
        if p:
            s.pin(p, hw + L, -i * GRID, pin_len, 180)
    for i, p in enumerate(top):
        if p:
            x = (i - (len(top) - 1) / 2) * GRID
            x = round(x / GRID) * GRID
            s.pin(p, x, y_top + L, pin_len, 270)
    for i, p in enumerate(bottom):
        if p:
            x = (i - (len(bottom) - 1) / 2) * GRID
            x = round(x / GRID) * GRID
            s.pin(p, x, y_bot - L, pin_len, 90)
    s.text(">NAME", -hw, y_top + 0.762 + (L if top else 0), 1.778, 95)
    s.text(">VALUE", -hw, y_bot - 2.54 - (L if bottom else 0), 1.778, 96)
    return s


class Device:
    def __init__(self, name, prefix, symbol, package, connects, description="", uservalue=True):
        self.name = name
        self.prefix = prefix
        self.symbol = symbol
        self.package = package
        self.connects = connects  # pin -> pad
        self.description = description
        self.uservalue = uservalue
        if package is not None:
            pads = set(package.pad_names())
            pins = set(p[0] for p in symbol.pins)
            for pin, pad in connects.items():
                assert pin in pins, (name, pin)
                assert pad in pads, (name, pad)
            assert set(connects) == pins, (name, pins - set(connects))

    def xml(self):
        e = etree.Element("deviceset", name=self.name, prefix=self.prefix,
                          uservalue="yes" if self.uservalue else "no")
        etree.SubElement(e, "description").text = self.description
        g = etree.SubElement(e, "gates")
        etree.SubElement(g, "gate", name="G$1", symbol=self.symbol.name, x="0", y="0")
        ds = etree.SubElement(e, "devices")
        d = etree.SubElement(ds, "device", name="")
        if self.package is not None:
            d.set("package", self.package.name)
            cs = etree.SubElement(d, "connects")
            for pin, pad in sorted(self.connects.items(), key=lambda kv: kv[0]):
                etree.SubElement(cs, "connect", gate="G$1", pin=pin, pad=pad)
        t = etree.SubElement(d, "technologies")
        etree.SubElement(t, "technology", name="")
        return e


class Library:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.packages = {}
        self.symbols = {}
        self.devices = {}

    def add(self, dev):
        if dev.package is not None:
            self.packages[dev.package.name] = dev.package
        self.symbols[dev.symbol.name] = dev.symbol
        assert dev.name not in self.devices, dev.name
        self.devices[dev.name] = dev
        return dev

    def xml(self, with_symbols=True, with_devices=True, only_packages=None):
        e = etree.Element("library", name=self.name)
        etree.SubElement(e, "description").text = self.description
        pk = etree.SubElement(e, "packages")
        for n in sorted(self.packages):
            if only_packages is None or n in only_packages:
                pk.append(self.packages[n].xml())
        if with_symbols:
            sy = etree.SubElement(e, "symbols")
            for n in sorted(self.symbols):
                sy.append(self.symbols[n].xml())
        if with_devices:
            dv = etree.SubElement(e, "devicesets")
            for n in sorted(self.devices):
                dv.append(self.devices[n].xml())
        return e


# ----------------------------------------------------------------------------- design
class Part:
    def __init__(self, name, dev, value, nets, sheet, group, dnp=False, note=""):
        self.name = name
        self.dev = dev
        self.value = value
        self.nets = nets      # pin -> net
        self.sheet = sheet
        self.group = group
        self.dnp = dnp
        self.note = note
        self.sch_xy = None
        self.brd_xy = None
        self.brd_rot = 0


class Design:
    def __init__(self, title, lib):
        self.title = title
        self.lib = lib
        self.parts = {}
        self.order = []
        self.sheets = []   # (title, [group names])
        self.notes = {}    # sheet index -> list of text lines
        self._cnt = {}

    def sheet(self, title):
        self.sheets.append(title)
        self.notes[len(self.sheets) - 1] = []
        return len(self.sheets) - 1

    reserved = {"U1", "J1", "J2", "J3", "J4", "J5", "J6", "JP1"}

    def next_name(self, prefix):
        while True:
            self._cnt[prefix] = self._cnt.get(prefix, 0) + 1
            name = "%s%d" % (prefix, self._cnt[prefix])
            if name not in self.reserved and name not in self.parts:
                return name

    def add(self, devname, value, nets, sheet, group, name=None, dnp=False, note=""):
        dev = self.lib.devices[devname]
        if name is None:
            name = self.next_name(dev.prefix)
        assert name not in self.parts, name
        pins = set(p[0] for p in dev.symbol.pins)
        for pin in nets:
            assert pin in pins, (name, devname, pin)
        p = Part(name, dev, value, dict(nets), sheet, group, dnp, note)
        self.parts[name] = p
        self.order.append(name)
        return p

    def netlist(self):
        nets = {}
        for pn in self.order:
            p = self.parts[pn]
            for pin, net in p.nets.items():
                if net is None:
                    continue
                nets.setdefault(net, []).append((pn, pin))
        return nets

    def pad_netlist(self):
        """net -> sorted list of (part, pad)."""
        out = {}
        for net, conns in self.netlist().items():
            out[net] = sorted((pn, self.parts[pn].dev.connects[pin]) for pn, pin in conns)
        return out
