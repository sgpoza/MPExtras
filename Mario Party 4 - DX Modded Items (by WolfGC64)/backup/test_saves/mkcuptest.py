#!/usr/bin/env python3
"""Build the Toad's Midway Madness cup test save from MARIPA4BOX0 (uses mkdxtest.build).

Checks the cup fix: DX's Gecko code used to set space 14's links to {82, 119},
removing the left cup's 0x200 exit (107), so CupObjRotate never found an exit
and the cups spun forever. The fixed DOL writes {82, 107}.

Toad's Midway Madness, turn 5/20, both cup arrows at their initial state
(board_data zeroed: cupDir = {0, 0}). Turn order and starting spaces:
  P1 (human) on 105 -> 106 (invisible) -> left cup 14. cupDir[1] = 0 needs the
     0x200 exit: this is the ride that softlocked before the fix.
  P2 (CPU)   on 105 -> left cup again, arrow now flipped: exit 82 (0x100).
  P3 (CPU)   on 123 -> 47 (invisible) -> right cup 2.
  P4 (CPU)   on 105 -> left cup a third time: back to the 107 exit, unless
     someone landed on 119 (the arrow-flip space) in between.
Any roll enters the cup on the first step (type-0 spaces don't use up a roll).
No items, so nobody detours. Star on space 91, Hidden Block on 76.
Usage: mkcuptest.py BOX0.gci OUTDIR [box]
"""
import struct, sys
from mkdxtest import build, SYS, SAVEDATA_END, NONE
from mkbonustest import finish

def main(tpl_path, outdir, box="2"):
    box = int(box)
    tpl = open(tpl_path, "rb").read()
    players = [(True, [NONE] * 3), (False, [NONE] * 3), (False, [NONE] * 3), (False, [NONE] * 3)]
    g = build(tpl, box, "Cup test (Toad)", players, turn=4, max_turn=20, board=0,
              star_pos=2, star_flag=0x04, star_total=1, block_pos=76,
              stars=[0, 0, 0, 0], coins=[30, 30, 30, 30],
              spaces=[(105, 16), (105, 16), (123, 48), (105, 16)])
    # Bonus Stars on, picks = Mini-Game/Coin/Happening (vanilla set), counters 0
    g = finish(g, sel=[0, 1, 2], items=[0] * 4, spent=[0] * 4, spaces=[0] * 4)
    b = bytearray(g)
    s = 0x40 + SYS
    b[s] &= ~0x40                              # no Team Battle
    b[s + 0x10:s + 0x13] = bytes([0, 0, 0])    # W01BoardWork: hostSide 0, cupDir {0, 0}
    b[s + 0xD4:s + 0xDC] = bytes(8)            # coin steal flag + text buffer
    ck = (~sum(b[0x40:0x40 + SAVEDATA_END])) & 0xFFFF
    struct.pack_into(">H", b, 0x40 + SAVEDATA_END, ck)
    path = f"{outdir}/01-GMPE-MARIPA4BOX{box}.gci"
    open(path, "wb").write(bytes(b))
    print("wrote", path)

if __name__ == "__main__":
    main(*sys.argv[1:4])
