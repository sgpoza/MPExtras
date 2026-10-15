import struct
def u32(d, o): return struct.unpack_from('>I', d, o)[0]
def parse(d):
    n = u32(d, 0)
    offs = [u32(d, 4 + 4*i) for i in range(n)]
    tbl = offs[0]
    pairs = [struct.unpack_from('>HH', d, tbl + 4*i) for i in range(n)]
    banks = {}
    for k in range(1, n):
        b = offs[k]
        end = offs[k+1] if k+1 < n else len(d)
        cnt = u32(d, b)
        mo = [u32(d, b + 4 + 4*i) for i in range(cnt)]
        msgs = []
        for i in range(cnt):
            s = b + mo[i]
            e = d.index(b'\0', s)
            msgs.append(d[s:e+1])
        banks[k] = (cnt, mo, msgs, b, end)
    return n, offs, pairs, banks
def show(m):
    out = ''
    i = 0
    while i < len(m):
        c = m[i]
        if c == 0: break
        if c in (0x1e, 0x1f): out += '{%02x %02x}' % (c, m[i+1]); i += 2; continue
        if c == 0x10: out += ' '
        elif c == 0x0a: out += '\n'
        elif c == 0xff: out += '[P]'
        elif 0x20 < c < 0x7f: out += chr(c)
        else: out += '{%02x}' % c
        i += 1
    return out
if __name__ == '__main__':
    import sys
    d = open(sys.argv[1], 'rb').read()
    n, offs, pairs, banks = parse(d)
    print(n, pairs[:3], pairs[-3:])
    for k in map(int, sys.argv[2:]):
        bid = [p for p in pairs if p[1] == k]
        cnt, mo, msgs, b, end = banks[k]
        print('== offs idx', k, 'bank', bid, 'at %x..%x cnt %d' % (b, end, cnt))
        for i, m in enumerate(msgs): print(i, repr(show(m)))
