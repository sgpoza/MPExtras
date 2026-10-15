"""Patch a clone of the bonus-stars ISO: duel codes into DX's code list (main.dol T3), FST moved, new board_e.dat."""
import struct, sys
iso, codes_fn, mess_fn = sys.argv[1:4]
codes = open(codes_fn, 'rb').read()
mess = open(mess_fn, 'rb').read()
DOL = 0x1e000
LIST_B = 0x1473B8          # DOL file offset of DX code list B
GL_HDR = 0x146984          # DOL file offset of GeckoLoader header (0x80147124)
NEW_FST = 0x1A0000
BOARD_E = 0x170000
with open(iso, 'r+b') as f:
    f.seek(0x420); dol, fo, fs, fmax = struct.unpack('>IIII', f.read(16))
    assert (dol, fo, fs) == (DOL, 0x16BA60, 0x2164)
    f.seek(DOL); hdr = bytearray(f.read(0x100))
    offs = list(struct.unpack_from('>18I', hdr, 0)); sizes = list(struct.unpack_from('>18I', hdr, 0x90))
    assert offs[3] == 0x146360 and sizes[3] == 0x7700
    f.seek(DOL + offs[3]); t3 = bytearray(f.read(sizes[3]))
    gl = GL_HDR - offs[3]
    total, unk, hsize, lsize = struct.unpack_from('>IIII', t3, gl)
    assert (total, hsize, lsize) == (0x70B8, 0xA18, 0x66A0)
    term = LIST_B - offs[3] + lsize - 8
    assert t3[term:term + 8] == bytes.fromhex('f000000000000000')
    new = t3[:term] + codes + t3[term:term + 8]
    S = len(codes)
    struct.pack_into('>I', new, gl, total + S)
    struct.pack_into('>I', new, gl + 12, lsize + S)
    while len(new) % 0x20: new += b'\0'
    end = DOL + offs[3] + len(new)
    assert end <= BOARD_E, hex(end)
    # move the FST first (the DOL grows over its old place)
    f.seek(fo); fst = bytearray(f.read(fs))
    f.seek(NEW_FST); assert not any(f.read(fs + 0x100))
    # board_e.dat entry: update its size in the FST copy
    n = struct.unpack_from('>I', fst, 8)[0]; strt = 12 * n
    found = 0
    for i in range(1, n):
        w0, a, b = struct.unpack_from('>III', fst, 12 * i)
        if (w0 >> 24) == 0 and a == BOARD_E:
            struct.pack_into('>I', fst, 12 * i + 8, len(mess)); found += 1
    assert found == 1
    assert BOARD_E + len(mess) <= NEW_FST
    f.seek(NEW_FST); f.write(fst)
    f.seek(0x424); f.write(struct.pack('>I', NEW_FST))
    # DOL: new T3 size + content (zero the rest of the old FST area)
    sizes[3] = len(new)
    struct.pack_into('>18I', hdr, 0x90, *sizes)
    f.seek(DOL); f.write(hdr)
    f.seek(DOL + offs[3]); f.write(new)
    f.write(bytes(BOARD_E - f.tell()))
    # message file
    f.seek(BOARD_E); f.write(mess)
    f.write(bytes(NEW_FST - f.tell()))
print('ok: codes %#x bytes, T3 %#x -> %#x, DOL ends %#x, FST at %#x' % (S, 0x7700, len(new), end, NEW_FST))
