import struct, sys
def fst(path):
    f = open(path, 'rb')
    f.seek(0x420); dol, fo, fs = struct.unpack('>III', f.read(12))
    f.seek(fo); d = f.read(fs)
    n = struct.unpack_from('>I', d, 8)[0]
    strt = 12*n
    def name(i):
        off = struct.unpack_from('>I', d, 12*i)[0] & 0xffffff
        e = d.index(b'\0', strt+off); return d[strt+off:e].decode()
    out = []
    def walk(i, end, prefix):
        while i < end:
            w0, a, b = struct.unpack_from('>III', d, 12*i)
            if w0 >> 24:
                walk(i+1, b, prefix + name(i) + '/'); i = b
            else:
                out.append((prefix + name(i), a, b, fo + 12*i)); i += 1
    walk(1, n, '')
    return dol, fo, fs, out
if __name__ == '__main__':
    dol, fo, fs, files = fst(sys.argv[1])
    print('dol %x fst %x size %x' % (dol, fo, fs))
    for p, a, b, e in sorted(files, key=lambda x: x[1]):
        if len(sys.argv) < 3 or sys.argv[2] in p: print('%08x %08x %08x %s' % (a, b, e, p))
