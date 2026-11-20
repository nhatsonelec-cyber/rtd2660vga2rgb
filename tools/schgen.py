"""Schematic writer: places library symbols, attaches net labels / power symbols
to every pin and writes KiCad 7 .kicad_sch files (root + flat sub-sheets)."""
import math, uuid, copy
from sexp import Sym, dump, find, first
import symlib

S = Sym
PROJECT = 'rtd2660vga2rgb'
POWER_SYMS = {'GND': 'GND', '+5V': '+5V', '+3V3': '+3V3', '+1V8': '+1V8'}
_ns = uuid.UUID('6f1e2c1a-4b7d-4a52-9c3e-2660a0b0c0d0')

def uid(*key):
    return str(uuid.uuid5(_ns, '/'.join(str(k) for k in key)))

def r2(v):
    return round(v + 0.0, 4)

FONT = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]

def effects(justify=None, hide=False, size=1.27):
    e = [S('effects'), [S('font'), [S('size'), size, size]]]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide:
        e.append(S('hide'))
    return e

class Comp:
    def __init__(self, ref, sym, value, fp, pins, sheet, at, rot=0, dnp=False, fields=None,
                 ref_at=None, val_at=None, hide_value=False, power_syms=True):
        self.ref, self.sym, self.value, self.fp = ref, sym, value, fp
        self.pins = {str(k): v for k, v in pins.items()}
        self.sheet, self.at, self.rot, self.dnp = sheet, at, rot, dnp
        self.fields = fields or {}
        self.ref_at, self.val_at, self.hide_value = ref_at, val_at, hide_value
        self.power_syms = power_syms

class Design:
    def __init__(self):
        self.comps = []
        self.texts = []      # (sheet, x, y, text, size)
        self.boxes = []      # (sheet, x1, y1, x2, y2)
        self.sheets = []     # (name, file, paper, title)
        self.extra_libs = {} # libname -> path
        self.flags = []      # (sheet, x, y, net)  PWR_FLAG placements

    def add(self, *a, **k):
        c = Comp(*a, **k)
        assert not any(x.ref == c.ref for x in self.comps), 'duplicate ' + c.ref
        self.comps.append(c)
        return c

    def netlist(self):
        """net -> sorted list of (ref, pin)"""
        nets = {}
        for c in self.comps:
            for p, n in c.pins.items():
                if n is None:
                    continue
                nets.setdefault(n, []).append((c.ref, p))
        return {n: sorted(v) for n, v in nets.items()}

def get_sym(d, libid):
    lib, name = libid.split(':')
    return symlib.get_symbol(lib, name, d.extra_libs.get(lib))

def xform(c, px, py):
    """library (y-up) point -> sheet coordinates for component c."""
    a = math.radians(c.rot)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    return r2(c.at[0] + rx), r2(c.at[1] - ry)

def out_dir(c, ang):
    """unit vector (sheet coords) pointing away from the body at the pin end."""
    a = math.radians(ang + c.rot)
    dx, dy = -math.cos(a), -math.sin(a)        # y-up frame
    return int(round(dx)), int(round(-dy))    # sheet frame (y down)

def wire(x1, y1, x2, y2, key):
    return [S('wire'), [S('pts'), [S('xy'), r2(x1), r2(y1)], [S('xy'), r2(x2), r2(y2)]],
            [S('stroke'), [S('width'), 0], [S('type'), S('default')]], [S('uuid'), S(uid('w', *key))]]

def glabel(net, x, y, d, key):
    ang = {(1, 0): 0, (-1, 0): 180, (0, -1): 90, (0, 1): 270}[d]
    just = 'left' if ang in (0, 90) else 'right'
    return [S('global_label'), net, [S('shape'), S('passive')], [S('at'), r2(x), r2(y), ang],
            effects(just), [S('uuid'), S(uid('gl', *key))],
            [S('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [S('at'), 0, 0, 0], effects(hide=True)]]

class SheetWriter:
    def __init__(self, d, name, file, paper, title, root_uuid, page):
        self.d, self.name, self.file, self.paper, self.title = d, name, file, paper, title
        self.uuid = uid('sheet', name)
        self.path = '/%s/%s' % (root_uuid, self.uuid)
        self.items, self.libsyms, self.pwr_n = [], {}, 0
        self.page = page

    def need(self, libid):
        if libid not in self.libsyms:
            self.libsyms[libid] = get_sym(self.d, libid)
        return self.libsyms[libid]

    def symbol_inst(self, libid, ref, value, fp, x, y, rot, pinnums, key, ref_at=None, val_at=None,
                    dnp=False, hide_ref=False, hide_value=False, extra=None, in_bom=True, ds='~'):
        e = [S('symbol'), [S('lib_id'), libid], [S('at'), r2(x), r2(y), rot], [S('unit'), 1],
             [S('in_bom'), S('yes' if in_bom else 'no')], [S('on_board'), S('yes')], [S('dnp'), S('yes' if dnp else 'no')],
             [S('uuid'), S(uid('sym', *key))]]
        ra = ref_at or (x + 2.54, y - 1.27, 0, 'left')
        va = val_at or (x + 2.54, y + 1.27, 0, 'left')
        if rot in (90, 270):
            ra = (ra[0], ra[1], 90 - ra[2], ra[3]); va = (va[0], va[1], 90 - va[2], va[3])
        e.append([S('property'), 'Reference', ref, [S('at'), r2(ra[0]), r2(ra[1]), ra[2]], effects(ra[3], hide_ref)])
        e.append([S('property'), 'Value', value, [S('at'), r2(va[0]), r2(va[1]), va[2]], effects(va[3], hide_value)])
        e.append([S('property'), 'Footprint', fp, [S('at'), r2(x), r2(y), 0], effects(hide=True)])
        e.append([S('property'), 'Datasheet', ds, [S('at'), r2(x), r2(y), 0], effects(hide=True)])
        for k, v in (extra or {}).items():
            e.append([S('property'), k, v, [S('at'), r2(x), r2(y), 0], effects(hide=True)])
        for n in pinnums:
            e.append([S('pin'), n, [S('uuid'), S(uid('pin', *key, n))]])
        e.append([S('instances'), [S('project'), PROJECT, [S('path'), self.path, [S('reference'), ref], [S('unit'), 1]]]])
        self.items.append(e)

    def power(self, net, x, y, d, key):
        """power symbol with its pin at (x,y); body points along d."""
        libid = 'power:' + POWER_SYMS[net]
        self.need(libid)
        self.pwr_n += 1
        if net == 'GND':
            rot = {(0, 1): 0, (1, 0): 90, (0, -1): 180, (-1, 0): 270}[d]
        else:
            rot = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}[d]
        ref = '#PWR%s%03d' % (self.page, self.pwr_n)
        va = (x + d[0] * 3.8, y + d[1] * 3.8 + (0 if d[0] == 0 else 0), 0, 'left' if d[0] > 0 else ('right' if d[0] < 0 else None))
        self.symbol_inst(libid, ref, net, '', x, y, rot, ['1'], key, ref_at=(x, y, 0, None), val_at=va,
                         hide_ref=True, in_bom=True)

    def flag(self, x, y, net, key):
        self.need('power:PWR_FLAG')
        self.pwr_n += 1
        ref = '#FLG%s%03d' % (self.page, self.pwr_n)
        self.symbol_inst('power:PWR_FLAG', ref, 'PWR_FLAG', '', x, y, 0, ['1'], key,
                         ref_at=(x, y - 1.9, 0, None), val_at=(x, y - 3.2, 0, None), hide_ref=True)
        self.items.append(wire(x, y, x, y + 2.54, key + ('fw',)))
        if net in POWER_SYMS:
            d = (0, 1)
            if net == 'GND':
                self.power(net, x, y + 2.54, d, key + ('fp',))
            else:
                self.items.append(glabel(net, x, y + 2.54, d, key + ('fl',)))
        else:
            self.items.append(glabel(net, x, y + 2.54, (0, 1), key + ('fl',)))

    def place(self, c):
        sym = self.need(c.sym)
        pl = symlib.pins(sym)
        nums = []
        done = {}
        for p in pl:
            n = p['number']
            if n in nums:
                continue
            nums.append(n)
            assert n in c.pins, '%s: pin %s (%s) not assigned' % (c.ref, n, p['name'])
            net = c.pins[n]
            x, y = xform(c, p['x'], p['y'])
            d = out_dir(c, p['angle'])
            if (x, y) in done:
                assert done[(x, y)] == net, '%s: stacked pins with different nets at pin %s' % (c.ref, n)
                continue
            done[(x, y)] = net
            key = (c.ref, n)
            if net is None:
                self.items.append([S('no_connect'), [S('at'), x, y], [S('uuid'), S(uid('nc', *key))]])
                continue
            vertical = d[0] == 0
            L = 2.54
            ex, ey = x + d[0] * L, y + d[1] * L
            self.items.append(wire(x, y, ex, ey, key))
            if net in POWER_SYMS and vertical and ((net == 'GND') == (d[1] > 0)) and (c.power_syms or net == 'GND'):
                self.power(net, ex, ey, d, key)
            else:
                self.items.append(glabel(net, ex, ey, d, key))
        missing = set(c.pins) - set(nums)
        assert not missing, '%s: unknown pins %s' % (c.ref, missing)
        fields = dict(c.fields)
        ds = symlib.prop(sym, 'Datasheet') or '~'
        self.symbol_inst(c.sym, c.ref, c.value, c.fp, c.at[0], c.at[1], c.rot, nums, (c.ref,),
                         ref_at=c.ref_at, val_at=c.val_at, dnp=c.dnp, hide_value=c.hide_value, extra=fields, ds=ds)

    def render(self, date, rev):
        d = self.d
        for c in d.comps:
            if c.sheet == self.name:
                self.place(c)
        for (sh, x, y, net) in d.flags:
            if sh == self.name:
                self.flag(x, y, net, ('flag', net, x, y))
        for (sh, x, y, t, size) in d.texts:
            if sh == self.name:
                self.items.append([S('text'), t, [S('at'), r2(x), r2(y), 0],
                                   [S('effects'), [S('font'), [S('size'), size, size]], [S('justify'), S('left'), S('bottom')]],
                                   [S('uuid'), S(uid('txt', sh, x, y, t))]])
        for (sh, x1, y1, x2, y2) in d.boxes:
            if sh == self.name:
                self.items.append([S('rectangle'), [S('start'), x1, y1], [S('end'), x2, y2],
                                   [S('stroke'), [S('width'), 0.15], [S('type'), S('dash')]],
                                   [S('fill'), [S('type'), S('none')]], [S('uuid'), S(uid('box', sh, x1, y1))]])
        tree = [S('kicad_sch'), [S('version'), 20230121], [S('generator'), S('eeschema')],
                [S('uuid'), S(self.uuid)], [S('paper'), self.paper],
                [S('title_block'), [S('title'), self.title], [S('date'), date], [S('rev'), rev],
                 [S('company'), 'rtd2660vga2rgb']],
                [S('lib_symbols')] + [self.libsyms[k] for k in sorted(self.libsyms)]]
        order = {'rectangle': 0, 'no_connect': 1, 'wire': 2, 'text': 3, 'global_label': 4, 'symbol': 5}
        tree += sorted(self.items, key=lambda e: order[str(e[0])])
        return dump(tree) + '\n'

def write_all(d, outdir, date, rev, root_title, root_notes):
    import os
    root_uuid = uid('root')
    files = {}
    sheets_e = []
    y = 40
    for i, (name, file, paper, title) in enumerate(d.sheets):
        sw = SheetWriter(d, name, file, paper, title, root_uuid, str(i + 2))
        files[file] = sw.render(date, rev)
        sheets_e.append([S('sheet'), [S('at'), 30, y], [S('size'), 60, 18], [S('fields_autoplaced')],
                         [S('stroke'), [S('width'), 0.1524], [S('type'), S('solid')]],
                         [S('fill'), [S('color'), 255, 255, 194, 1.0]], [S('uuid'), S(sw.uuid)],
                         [S('property'), 'Sheetname', title, [S('at'), 30, y - 0.7, 0], effects('left bottom')],
                         [S('property'), 'Sheetfile', file, [S('at'), 30, y + 18.6, 0], effects('left top')],
                         [S('instances'), [S('project'), PROJECT, [S('path'), '/' + root_uuid, [S('page'), str(i + 2)]]]]])
        y += 32
    root = [S('kicad_sch'), [S('version'), 20230121], [S('generator'), S('eeschema')], [S('uuid'), S(root_uuid)],
            [S('paper'), 'A4'],
            [S('title_block'), [S('title'), root_title], [S('date'), date], [S('rev'), rev], [S('company'), 'rtd2660vga2rgb']],
            [S('lib_symbols')]]
    ty = 30
    for line in root_notes:
        root.append([S('text'), line, [S('at'), 110, ty, 0],
                     [S('effects'), [S('font'), [S('size'), 1.8, 1.8]], [S('justify'), S('left'), S('bottom')]],
                     [S('uuid'), S(uid('rtxt', ty))]])
        ty += 4.5
    root += sheets_e
    root.append([S('sheet_instances'), [S('path'), '/', [S('page'), '1']]])
    files[PROJECT + '.kicad_sch'] = dump(root) + '\n'
    for f, t in files.items():
        open(os.path.join(outdir, f), 'w', encoding='utf8').write(t)
    return files
