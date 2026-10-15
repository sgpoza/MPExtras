import struct, sys
def lz(src, size):
    tb = bytearray(1024); pos = 958; out = bytearray(); s = 0; flag = 0
    while len(out) < size:
        flag >>= 1
        if not flag & 0x100:
            flag = src[s] | 0xFF00; s += 1
        if flag & 1:
            out.append(src[s]); tb[pos] = src[s]; s += 1; pos = (pos + 1) & 0x3FF
        else:
            i = src[s]; c = src[s+1]; s += 2
            i |= (c & ~0x3F) << 2; c = (c & 0x3F) + 3
            for j in range(c):
                v = tb[(i + j) & 0x3FF]; out.append(v); tb[pos] = v; pos = (pos + 1) & 0x3FF
    return bytes(out[:size])
def slide(src, size, fs):
    s = 4; out = bytearray(); fl = 0; flag = 0
    while len(out) < size:
        if fl == 0:
            flag = struct.unpack_from('>I', src, s)[0]; s += 4; fl = 32
        if flag >> 31:
            out.append(src[s]); s += 1
        else:
            d = (src[s] << 8) | src[s+1]; s += 2
            ln = (d >> 12) & 0xF; d &= 0xFFF
            if ln == 0: ln = src[s] + 18; s += 1
            else: ln += 2
            st = len(out) - d
            for k in range(ln):
                idx = st + k - 1
                out.append(out[idx] if (fs or idx >= 0) and idx < len(out) else 0)
        flag = (flag << 1) & 0xFFFFFFFF; fl -= 1
    return bytes(out[:size])
def rle(src, size):
    out = bytearray(); s = 0
    while len(out) < size:
        n = src[s]; s += 1
        if n < 128: out += bytes([src[s]]) * n; s += 1
        else: n -= 128; out += src[s:s+n]; s += n
    return bytes(out)
def get(arc, n):
    off = struct.unpack_from('>I', arc, 4 + n*4)[0]
    raw, typ = struct.unpack_from('>II', arc, off)
    d = arc[off+8:]
    return {0: lambda: d[:raw], 1: lambda: lz(d, raw), 2: lambda: slide(d, raw, False),
            3: lambda: slide(d, raw, True), 4: lambda: slide(d, raw, True), 5: lambda: rle(d, raw)}[typ]()
def spaces(data):
    cnt = struct.unpack_from('>I', data)[0]; o = 4; out = []
    for i in range(cnt):
        pos = struct.unpack_from('>3f', data, o); o += 36
        flag, typ, lc = struct.unpack_from('>IHH', data, o); o += 8
        links = [x + 1 for x in struct.unpack_from('>%dH' % lc, data, o)]; o += 2*lc
        out.append(dict(id=i+1, pos=pos, flag=flag, type=typ, links=links))
    return out
if __name__ == '__main__':
    arc = open(sys.argv[1], 'rb').read()
    sp = spaces(get(arc, 0))
    print('count', len(sp))
    for s in sp:
        print('%3d type=%d flag=%08x links=%s pos=(%.0f,%.0f,%.0f)' % (s['id'], s['type'], s['flag'], s['links'], *s['pos']))
