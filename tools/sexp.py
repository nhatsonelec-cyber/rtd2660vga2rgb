"""Minimal S-expression reader/writer for KiCad files."""
import re

class Sym(str):
    """Unquoted atom."""
    pass

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))')

def parse(text):
    pos = 0
    stack = [[]]
    n = len(text)
    while True:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            top = stack.pop()
            stack[-1].append(top)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3).replace('\\"', '"').replace('\\\\', '\\'))
        else:
            stack[-1].append(Sym(m.group(4)))
    return stack[0][0]

def _atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, str):
        return '"' + a.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(a, float):
        s = ('%.4f' % a).rstrip('0').rstrip('.')
        return s if s not in ('', '-0') else '0'
    return str(a)

def dump(e, ind=0):
    if not isinstance(e, list):
        return _atom(e)
    flat = '(' + ' '.join(dump(x) for x in e) + ')'
    if len(flat) < 110 and '\n' not in flat:
        return flat
    pad = '  ' * (ind + 1)
    out = '(' + _atom(e[0])
    i = 1
    while i < len(e) and not isinstance(e[i], list):
        out += ' ' + _atom(e[i]); i += 1
    for x in e[i:]:
        out += '\n' + pad + dump(x, ind + 1)
    out += '\n' + '  ' * ind + ')'
    return out

def find(e, name):
    return [x for x in e if isinstance(x, list) and x and x[0] == name]

def first(e, name):
    r = find(e, name)
    return r[0] if r else None
