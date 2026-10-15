"""Append bank 57 (Last 5 Turns coin steal) to board_e.dat."""
import struct, re, sys, mess
CH = {' ': 0x10, '\n': 0x0A, ',': 0x82, '.': 0x85, '!': 0xC2, '?': 0xC3, "'": 0x5C, '-': 0x3D}
def enc(s):
    out = bytearray()
    for tok in re.findall(r'\{[0-9a-f ]+\}|\[P\]|.', s, re.S):
        if tok == '[P]': out.append(0xFF)
        elif tok.startswith('{'): out += bytes(int(x, 16) for x in tok[1:-1].split())
        elif tok in CH: out.append(CH[tok])
        else:
            assert 0x20 < ord(tok) < 0x7F, tok; out.append(ord(tok))
    return bytes(out) + b'\0'
N = lambda k: '{1e 05}{1f %02x}{1e 08}' % k   # character name insert
INTRO = '{0b}' + N(1) + ' landed on ' + N(2) + "'s space!\nIn the {1e 03}Last 5 Turns{1e 08}, that means...[P]"
MSGS = [
    INTRO + N(1) + ' steals {1e 05}{1f 03} coin]s^{1e 08}\nfrom ' + N(2) + '![P]',
    INTRO + N(1) + ' steals {1e 05}10 coins{1e 08}\nfrom ' + N(2) + '...[P]But wait!\n' + N(2) + " doesn't have\na single coin![P]",
]

I = '{20}{20}{20}{20}'   # host portrait indent (4 x 20px)
def host(expr, *pages):
    return '{0b}{1c}{%02x}' % expr + ''.join('\n'.join(I + l for l in p) + '[P]' for p in pages)
C10 = '{1e 05}10 coins{1e 08}'
HOSTS = [  # Last Five Turns Event announcement, one per board host (msg 2 + board)
    host(0x01, ["Oh, and one more thing!"],
               ["From now on, if you land on a", "space where a rival is standing,", "you'll steal " + C10 + " from them!"],
               ["So keep an eye on where", "everybody is standing!"]),
    host(0x04, ["Hoo-wee! Hold on, there's more!"],
               ["From now on, land on a space", "where a rival is standing, and", "you'll swipe " + C10 + " from them!"],
               ["Coins changing hands... Now", "that's my kind of game!"]),
    host(0x07, ["Ooh... Um, one more thing,", "if you don't mind..."],
               ["If you land on a space where", "a rival is standing, you'll", "take " + C10 + " from them..."],
               ["That sounds a little scary...", "Please be careful, OK?"]),
    host(0x0A, ["Ee hee! And now, a little", "something extra..."],
               ["Land on a space where a rival", "is standing, and you'll steal", C10 + " from them!"],
               ["Stealing is SO much fun!", "Trust me, I would know!"]),
    host(0x0D, ["Oh my, I nearly forgot..."],
               ["From now on, should you stop on", "a space where a rival stands,", "you will take " + C10 + " from them."],
               ["Do mind where everyone is", "standing, young ones."]),
    host(0x10, ["Gwa ha ha! And now for MY rule!"],
               ["Land on a space where a rival", "is standing, and you steal", C10 + " from that loser!"],
               ["Take everything you can get!", "Gwa ha ha ha ha!"]),
]
MSGS += HOSTS
BANK = 57
def build(d):
    n, offs, pairs, banks = mess.parse(d)
    assert n == 58 and pairs[-1] == (0, 0) and max(p[0] for p in pairs) == 56
    n2 = n + 1
    tbl = 4 + 4 * n2
    assert tbl + 4 * n2 <= offs[1]
    bank_off = (len(d) + 3) & ~3
    body = bytearray(struct.pack('>I', len(MSGS)) + bytes(4 * len(MSGS)))
    for i, m in enumerate(MSGS):
        struct.pack_into('>I', body, 4 + 4 * i, len(body)); body += enc(m)
    while len(body) % 4: body.append(0)
    out = bytearray(d) + bytes(bank_off - len(d)) + body
    struct.pack_into('>I', out, 0, n2)
    struct.pack_into('>%dI' % n2, out, 4, tbl, *offs[1:], bank_off)
    newpairs = pairs[:-1] + [(BANK, n2 - 1), (0, 0)]
    out[tbl:offs[1]] = bytes(offs[1] - tbl)
    for i, p in enumerate(newpairs): struct.pack_into('>HH', out, tbl + 4 * i, *p)
    # every old bank must still parse byte-identical
    n3, offs3, pairs3, banks3 = mess.parse(bytes(out))
    for k in range(1, n): assert banks3[k][2] == banks[k][2]
    return bytes(out)
if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    out = build(d)
    open(sys.argv[2], 'wb').write(out)
    n, offs, pairs, banks = mess.parse(out)
    print('size %x -> %x' % (len(d), len(out)), pairs[-3:])
    for m in banks[n - 1][2]: print(repr(mess.show(m)))
