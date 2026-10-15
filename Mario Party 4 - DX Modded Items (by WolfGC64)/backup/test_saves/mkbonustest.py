#!/usr/bin/env python3
"""Build the Random Bonus Stars test saves from MARIPA4BOX0 (uses mkdxtest.build).

BOX1 "Bonus Stars: start": new Party game on Toad's Midway Madness (Bonus Stars on).
      Continue runs the opening; the host announces 3 random Bonus Stars after
      the turn order.
BOX2 "Bonus Stars: end": Goomba's Greedy Gala right after the last turn's
      Mini-Game (turn 20/20). Continue ends the game and goes to the results:
      Item Star (P1 wins), Slow Star (P2/P3 tie), Bowser Star (nobody landed on
      a Bowser Space).
Usage: mkbonustest.py BOX0.gci OUTDIR
"""
import struct, sys
from mkdxtest import build, SYS, PLY, SAVEDATA_END, NONE

STATE = SYS + 0x98          # GWSystem+0x98 = 0x8018FD90 (see bonusstars.py)
ITEM, SLOW, BOWSER = 3, 6, 8

def finish(gci, bonus=True, sel=None, items=None, spent=None, spaces=None, per_player=None):
    g = bytearray(gci); b = memoryview(g)[0x40:]
    w = struct.unpack_from(">H", b, SYS + 0x02)[0]
    w = (w | 0x8000) if bonus else (w & 0x7FFF)       # Bonus Stars option
    struct.pack_into(">H", b, SYS + 0x02, w)
    b[STATE:STATE + 0x18] = bytes(0x18)
    if sel:
        b[STATE:STATE + 4] = bytes([s + 1 for s in sel] + [0xB5])
        b[STATE + 4:STATE + 8] = bytes(items)
        struct.pack_into(">4H", b, STATE + 0x08, *spent)
        struct.pack_into(">4H", b, STATE + 0x10, *spaces)
    for i, fields in enumerate(per_player or []):
        p = PLY + i * 0x30
        for off, fmt, val in fields:
            struct.pack_into(fmt, b, p + off, val)
    ck = (~sum(b[:SAVEDATA_END])) & 0xFFFF
    struct.pack_into(">H", b, SAVEDATA_END, ck)
    return bytes(g)

def main(tpl_path, outdir):
    tpl = open(tpl_path, "rb").read()
    players = [(True, [NONE] * 3), (False, [NONE] * 3), (False, [NONE] * 3), (False, [NONE] * 3)]

    start = build(tpl, 1, "Bonus Stars: start", players, turn=1, max_turn=20, coins=0, board=0, fresh=True)
    start = finish(start)

    end = build(tpl, 2, "Bonus Stars: end", players, turn=20, max_turn=20, board=1,
                star_pos=2, star_flag=0x05, star_total=4, block_pos=57,
                stars=[3, 2, 2, 1], coins=[45, 60, 30, 80],
                spaces=[(18, 17), (40, 39), (63, 62), (74, 73)])
    # per player: coins_mg, red_count, question_count, bowser_count (bowser = 0 for everybody)
    stats = [(120, 4, 3), (85, 6, 2), (140, 3, 5), (60, 7, 1)]
    end = finish(end, sel=[ITEM, SLOW, BOWSER],
                 items=[5, 2, 2, 1], spent=[25, 10, 10, 30], spaces=[62, 48, 48, 70],
                 per_player=[[(0x1E, ">h", mg), (0x15, ">b", red), (0x16, ">b", q), (0x18, ">b", 0)]
                             for mg, red, q in stats])
    for box, data in ((1, start), (2, end)):
        path = f"{outdir}/01-GMPE-MARIPA4BOX{box}.gci"
        open(path, "wb").write(data)
        print("wrote", path)

if __name__ == "__main__":
    main(*sys.argv[1:3])
