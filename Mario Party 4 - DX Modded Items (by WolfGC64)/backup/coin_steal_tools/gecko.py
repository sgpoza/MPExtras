import struct, sys, dol
def parse(words):
    i = 0; out = []
    while i + 1 < len(words):
        a, b = words[i], words[i+1]; t = a >> 24 & 0xFE
        if a == 0x00D0C0DE: i += 2; continue
        if a == 0xF0000000: break
        addr = 0x80000000 | (a & 0x01FFFFFF)
        if t == 0xC2: out.append(('C2', addr, b)); i += 2 + 2*b
        elif t in (0x04, 0x02, 0x00): out.append(('%02X' % t, addr, b)); i += 2
        elif t == 0x06: out.append(('06', addr, b)); i += 2 + 2*((b+7)//8)
        elif t in (0x20, 0x22, 0x28, 0x2A, 0xE0, 0xE2): out.append(('%02X' % t, addr, b)); i += 2
        elif t == 0xC0: out.append(('C0', 0, b)); i += 2 + 2*b
        else: out.append(('??%02X' % t, addr, b)); i += 2
    return out
if __name__ == '__main__':
    f = open(sys.argv[1], 'rb'); f.seek(0x1e000 + 0x1473B8); d = f.read(0x6000)
    w = struct.unpack('>%dI' % (len(d)//4), d)
    S = dol.syms()
    for t, a, b in parse(w):
        s = dol.symat(S, a) if t not in ('C0',) else ''
        print(t, '%08x' % a, '%08x' % b, s, ('+0x%x' % (a - S[s][0])) if s else '')
