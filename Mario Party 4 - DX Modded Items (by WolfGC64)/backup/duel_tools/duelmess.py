"""Duel texts: rewrite bank 57 msgs 2-7 (Last 5 host lines) and add bank 58 (Bob-omb duel)."""
import struct, re, sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-sgpoza-Documents-Decomp-marioparty4/1cb775f1-1fdc-4b10-bb05-edd15e77e95a/scratchpad/tools')
import mess
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
I = '{20}{20}{20}{20}'          # portrait indent
C = '{20}{20}{20}{20}{20}{20}{0f}'  # menu choice
N = lambda k: '{1e 05}{1f %02x}{1e 08}' % k
DUEL = '{1e 03}Duel{1e 08}'
STAR = '{1e 07}Star{1e 08}'
STARS = '{1e 07}Stars{1e 08}'
def talk(*pages, expr=None):
    head = '{0b}' + ('{1c}{%02x}' % expr if expr is not None else '')
    return head + ''.join('\n'.join(I + l for l in p) + '[P]' for p in pages)
def menu(question, *choices):
    return '{0b}' + I + question + ''.join('\n' + C + c for c in choices)
def host(expr, *pages): return talk(*pages, expr=expr)

HOSTS = [  # bank 57 msgs 2..7 (board 0..5 host, end of the Last Five Turns Event)
    host(0x01, ["Oh, and one more thing!"],
               ["From now on, if you land on a", "space where a rival is standing,", "you'll challenge them to a " + DUEL + "!"],
               ["You can bet coins or even", STARS + "! Good luck, everybody!"]),
    host(0x04, ["Hoo-wee! Hold on, there's more!"],
               ["From now on, land on a space", "where a rival is standing, and", "it's " + DUEL + " time!"],
               ["Betting coins and " + STARS + "... Now", "that's my kind of game!"]),
    host(0x07, ["Ooh... Um, one more thing,", "if you don't mind..."],
               ["If you land on a space where", "a rival is standing, you'll", "have to fight a " + DUEL + "..."],
               ["Coins or even " + STARS + " are at", "stake... Please be careful, OK?"]),
    host(0x0A, ["Ee hee! And now, a little", "something extra..."],
               ["Land on a space where a rival", "lurks, and you'll have to fight", "a " + DUEL + "!"],
               ["Coins... " + STARS + "... Whoever loses,", "loses big! Ee hee hee!"]),
    host(0x0D, ["Oh my, I nearly forgot..."],
               ["From now on, should you stop on", "a space where a rival stands,", "you will challenge them to a " + DUEL + "."],
               ["Coins and even " + STARS + " may be", "wagered. Do be careful!"]),
    host(0x10, ["Gwa ha ha! And now for MY rule!"],
               ["Land on a space where a rival", "is standing, and you " + DUEL + "!"],
               ["The winner takes the coins", "or " + STARS + "! Gwa ha ha ha!"]),
]
MGNAMES = ["Bowser Bop", "Mystic Match 'Em", "Archaeologuess", "Goomba's Chip Flip",
           "Kareening Koopas", "Bowser Wrestling", "Panels of Doom"]
B58 = {
    0: talk(["Kaboom! " + N(1) + " landed on", N(2) + "'s space!"],
            ["In the {1e 03}Last 5 Turns{1e 08}, that means", "it's time for a " + DUEL + "!"]),
    1: menu("What will you bet?", "Coins", "1 " + STAR + " for 40 coins", "1 " + STAR),
    2: menu("How many coins?", "10 coins", "20 coins", "Half of " + N(1) + "'s ({1f 03})",
            "All of " + N(1) + "'s ({1f 04})"),
    3: menu("Who will you challenge?", '{1f 01}', '{1f 02}'),
    4: menu("Who will you challenge?", '{1f 01}', '{1f 02}', '{1f 03}'),
    5: menu("Pick the Duel Mini-Game!", '{1f 01}', '{1f 02}'),
    6: talk([N(1) + " bets {1e 05}{1f 03} coin]s^{1e 08} and", N(2) + " bets {1e 05}{1f 04} coin]s^{1e 08}!", "The winner takes it all!"]),
    7: talk([N(1) + " bets {1e 05}40 coins{1e 08} and", N(2) + " bets {1e 05}1{1e 08} " + STAR + "!", "The winner takes it all!"]),
    8: talk([N(1) + " and " + N(2), "each bet {1e 05}1{1e 08} " + STAR + "!", "The winner takes it all!"]),
    9: talk(["Wait a sec... You two don't", "have anything you can bet!"], ["No " + DUEL + " this time.", "See ya!"]),
    10: talk(["The Duel Mini-Game is", "{1e 03}{1f 03}{1e 08}!"], ["Ready? Let the " + DUEL + " begin!"]),
    11: talk(["The two of them settle it", "far away from here..."], ["...Boom! It's over!"]),
    12: talk(["And the winner is...", N(1) + "!"]),
    13: talk(["It's a tie!", "Everybody keeps what they bet."]),
    14: talk([N(1) + " wins {1e 05}{1f 03} coin]s^{1e 08}", "from " + N(2) + "!"]),
    15: talk([N(1) + " takes {1e 05}1{1e 08} " + STAR, "from " + N(2) + "!"]),
    16: talk(["What a blast! See ya next time!"]),
}
for k, n in enumerate(MGNAMES): B58[20 + k] = n
B58_LIST = [B58.get(i, '{0b}') for i in range(max(B58) + 1)]

def rebuild(d):
    n, offs, pairs, banks = mess.parse(d)
    order = [(b, banks[k][2]) for b, k in pairs if k]   # (bank id, msgs) in file order
    ids = [b for b, _ in order]
    assert ids[-1] == 57 and 58 not in ids
    i57 = ids.index(57)
    msgs57 = list(order[i57][1]); assert len(msgs57) == 8
    for h in range(6): msgs57[2 + h] = enc(HOSTS[h])
    order[i57] = (57, msgs57)
    order.append((58, [enc(m) for m in B58_LIST]))
    cnt = len(order) + 1
    tbl = 4 + 4 * cnt
    first = (tbl + 4 * cnt + 15) & ~15
    out = bytearray(first)
    offsets = [tbl]
    for b, msgs in order:
        while len(out) % 4: out.append(0)
        start = len(out); offsets.append(start)
        body = bytearray(struct.pack('>I', len(msgs)) + bytes(4 * len(msgs)))
        for i, m in enumerate(msgs):
            struct.pack_into('>I', body, 4 + 4 * i, len(body)); body += m
        out += body
    while len(out) % 4: out.append(0)
    struct.pack_into('>I', out, 0, cnt)
    struct.pack_into('>%dI' % cnt, out, 4, *offsets)
    for i, (b, _) in enumerate(order): struct.pack_into('>HH', out, tbl + 4 * i, b, i + 1)
    struct.pack_into('>HH', out, tbl + 4 * len(order), 0, 0)
    # verify every bank parses back identically
    n2, offs2, pairs2, banks2 = mess.parse(bytes(out))
    got = {b: banks2[k][2] for b, k in pairs2 if k}
    for b, msgs in order: assert got[b] == list(msgs), b
    old = {b: banks[k][2] for b, k in pairs if k}
    for b in old:
        if b != 57: assert got[b] == old[b], b
    return bytes(out)

def width_check():
    def lines(m):
        m = m[:-1]; i = 0; res = []; buf = bytearray()
        while i < len(m):
            c = m[i]
            if c in (0x1e, 0x1f, 0x1c): i += 2; continue
            if c in (0x0a, 0xff, 0x0b): 
                if buf: res.append(bytes(buf))
                buf = bytearray(); i += 1; continue
            buf.append(c); i += 1
        if buf: res.append(bytes(buf))
        return res
    worst = 0
    for name, m in [('h%d' % i, enc(x)) for i, x in enumerate(HOSTS)] + [('b%d' % k, enc(v)) for k, v in B58.items() if k < 20]:
        for l in lines(m):
            if not (l.startswith(b'\x20' * 4)):
                print('NOT INDENTED', name, l); 
            w = len(l.lstrip(b'\x20').lstrip(b'\x0f')); worst = max(worst, w)
            if w > 34: print('LONG', name, w, l)
    print('max width', worst)

if __name__ == '__main__':
    width_check()
    d = open(sys.argv[1], 'rb').read()
    out = rebuild(d)
    open(sys.argv[2], 'wb').write(out)
    print('size %x -> %x' % (len(d), len(out)))
