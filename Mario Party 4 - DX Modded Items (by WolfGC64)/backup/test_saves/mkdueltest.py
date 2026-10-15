#!/usr/bin/env python3
"""Build the Last 5 Turns Duels test saves from MARIPA4BOX0 (uses mkdxtest.build / mkbonustest.finish).

Both: Goomba's Greedy Gala, 20 turns, P1 (human, first in turn order) on space 18 with a
Slow Block, 50 coins and 1 Star; P2 (CPU) on space 20 with 35 coins and 2 Stars, 3 spaces
ahead (18 -> 19 -> 21 -> 20, no events on the way). With these numbers every bet is
available: Coins, 1 Star for 40 coins and 1 Star. Use the Slow Block and stop on a 3.
BOX1 "Duel: turn 15" -> plays turn 15/20 (not Last 5): no duel must happen.
BOX2 "Duel: Last 5"  -> plays turn 16/20: Last Five Turns Event (host announces duels),
      then P1's turn; landing on P2 starts the duel.
Usage: mkdueltest.py BOX0.gci OUTDIR
"""
import struct, sys
from mkdxtest import build, SYS, SAVEDATA_END, NONE
from mkbonustest import finish

SLOW = 0x1F

def main(tpl_path, outdir):
    tpl = open(tpl_path, "rb").read()
    players = [(True, [SLOW, NONE, NONE]), (False, [NONE] * 3), (False, [NONE] * 3), (False, [NONE] * 3)]
    opts = dict(max_turn=20, board=1, star_pos=2, star_flag=0x05, star_total=4, block_pos=57,
                stars=[1, 2, 1, 0], coins=[50, 35, 25, 40],
                spaces=[(18, 17), (20, 21), (63, 62), (74, 73)])
    for box, turn, label in ((1, 14, "Duel: turn 15"), (2, 15, "Duel: Last 5")):
        g = build(tpl, box, label, players, turn=turn, **opts)
        g = finish(g, sel=[0, 1, 2], items=[0] * 4, spent=[0] * 4, spaces=[0] * 4)
        b = bytearray(g)
        s = 0x40 + SYS
        b[s] &= ~0x40                              # no Team Battle
        b[s + 0x02] |= 0x20                        # show COM mini-games on
        b[s + 0xB0:s + 0xDC] = bytes(0x2C)         # duel state + old steal bytes
        ck = (~sum(b[0x40:0x40 + SAVEDATA_END])) & 0xFFFF
        struct.pack_into(">H", b, 0x40 + SAVEDATA_END, ck)
        path = f"{outdir}/01-GMPE-MARIPA4BOX{box}.gci"
        open(path, "wb").write(bytes(b))
        print("wrote", path)

if __name__ == "__main__":
    main(*sys.argv[1:3])
