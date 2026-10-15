import struct, re
SYMS = '/Users/sgpoza/Documents/Decomp/marioparty4/config/GMPE01_01/symbols.txt'
def load(path, off=0):
    f = open(path, 'rb'); f.seek(off); h = f.read(0x100)
    offs = struct.unpack_from('>18I', h, 0); addrs = struct.unpack_from('>18I', h, 0x48); sizes = struct.unpack_from('>18I', h, 0x90)
    secs = []
    for o, a, s in zip(offs, addrs, sizes):
        if s: f.seek(off + o); secs.append((a, s, f.read(s), o))
    return secs
def read(secs, addr, n):
    for a, s, d, o in secs:
        if a <= addr < a + s: return d[addr-a:addr-a+n]
def syms():
    out = {}
    for l in open(SYMS):
        m = re.match(r'(\S+) = \.\w+:0x([0-9A-F]+); // type:(\w+)(?: size:0x([0-9A-F]+))?', l)
        if m: out[m.group(1)] = (int(m.group(2), 16), int(m.group(4) or '0', 16))
    return out
def symat(S, addr):
    best = None
    for k, (a, s) in S.items():
        if a <= addr < a + max(s, 1) and (best is None or a > S[best][0]): best = k
    return best
