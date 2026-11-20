"""Load symbols from KiCad symbol libraries, resolve 'extends', list pins."""
import os, copy
from sexp import parse, Sym, find, first

SYMDIR = '/usr/share/kicad/symbols'
_cache = {}

def load_lib(lib, path=None):
    if lib not in _cache:
        p = path or os.path.join(SYMDIR, lib + '.kicad_sym')
        tree = parse(open(p, encoding='utf8').read())
        _cache[lib] = {s[1]: s for s in find(tree, 'symbol')}
    return _cache[lib]

def get_symbol(lib, name, path=None):
    """Return a flattened symbol s-expr named 'lib:name' (extends resolved)."""
    d = load_lib(lib, path)
    s = copy.deepcopy(d[name])
    ext = first(s, 'extends')
    if ext:
        base = copy.deepcopy(d[ext[1]])
        bname = base[1]
        # rename sub-units
        for u in find(base, 'symbol'):
            u[1] = name + u[1][len(bname):]
        props = {p[1]: p for p in find(s, 'property')}
        out = []
        for x in base:
            if isinstance(x, list) and x[0] == 'property' and x[1] in props:
                out.append(props.pop(x[1]))
            else:
                out.append(x)
        # extra props of derived symbol: insert before first sub-symbol
        idx = next((i for i, x in enumerate(out) if isinstance(x, list) and x[0] == 'symbol'), len(out))
        for p in props.values():
            out.insert(idx, p); idx += 1
        out[1] = name
        s = out
    s[1] = lib + ':' + name
    return s

def pins(sym):
    """Return list of dicts: number,name,x,y,angle,length,unit,etype."""
    res = []
    for u in find(sym, 'symbol'):
        parts = u[1].rsplit('_', 2)
        unit = int(parts[-2])
        for p in find(u, 'pin'):
            at = first(p, 'at')
            res.append(dict(number=first(p, 'number')[1], name=first(p, 'name')[1],
                            x=float(at[1]), y=float(at[2]), angle=int(float(at[3])) if len(at) > 3 else 0,
                            length=float(first(p, 'length')[1]), unit=unit, etype=str(p[1])))
    return res

def prop(sym, name):
    for p in find(sym, 'property'):
        if p[1] == name:
            return p[2]
    return ''
