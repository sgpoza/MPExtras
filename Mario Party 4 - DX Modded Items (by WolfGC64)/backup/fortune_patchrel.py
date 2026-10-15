"""Rebalance Reversal of Fortune stage 3: move bumpers 2-4 (lbl_1_data_264 / lbl_1_data_2A0) in m444dll.rel."""
import struct, sys
DATA = 0xE448  # .data section file offset (section 5)
NEW = {  # bumper: (start x, start y, slide min x, slide max x)
    2: (-120, -302, -120, -119),
    3: (-19, -415, -54, -6),
    4: (-30, -294, -37, 18),
}
OLD = {2: (-75, -300, -100, -60), 3: (25, -300, 10, 50), 4: (-25, -400, -50, 0)}
r = bytearray(open(sys.argv[1], 'rb').read())
assert len(r) == 105820
for i, (x, y, lo, hi) in NEW.items():
    pos, rng = DATA + 0x264 + i * 12, DATA + 0x2A0 + i * 8
    ox, oy, olo, ohi = OLD[i]
    assert struct.unpack_from('>3f', r, pos) == (ox, oy, 0) and struct.unpack_from('>2f', r, rng) == (olo, ohi), i
    struct.pack_into('>3f', r, pos, x, y, 0)
    struct.pack_into('>2f', r, rng, lo, hi)
open(sys.argv[2], 'wb').write(r)
print('patched', sys.argv[2])
