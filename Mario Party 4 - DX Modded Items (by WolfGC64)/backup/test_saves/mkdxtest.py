#!/usr/bin/env python3
"""Build MP4 DX test saves (MARIPA4BOX1/2) from an existing MARIPA4BOX0 GCI.

By default a box holds a party game in progress on the template's board, saved
right after a minigame (flag 1:2 set), so "Continue" resumes at the next turn.
board=N moves the game to board N. With fresh=True it is a new game (state as
left by BoardSaveInit, flags 1:0/1:1 clear), so the board runs its normal
opening. Otherwise it stays mid-game and needs valid board-N state: star_pos,
star_flag, star_total, block_pos and per-player (space_curr, space_prev).
Space IDs come from file 0 of data/wNN.bin (see spaces.py).
"""
import struct, sys

SPEED, WARP, CHARM, NONE = 0x1E, 0x1A, 0x15, 0xFF  # CHARM = Chance Time Charm (DX: starts Reversal of Fortune)

GCI_HDR = 0x40
STAT = 0x2040            # GameStat
SYS = 0x2158             # party SystemState (0xDC)
PLY = SYS + 0xDC         # party PlayerState[4] (0x30 each)
SAVEDATA_END = 0x2490    # checksum (u16 BE) follows SaveBufData

def build(tpl, box, label, players, turn=1, max_turn=30, coins=50, board=None, fresh=False,
          star_pos=0, star_flag=1, star_total=1, block_pos=0, spaces=None, stars=None):
    gci = bytearray(tpl)
    hdr, b = gci[:GCI_HDR], memoryview(gci)[GCI_HDR:]

    name = b"MARIPA4BOX%d" % box
    hdr[0x08:0x28] = name.ljust(32, b"\0")
    gci[:GCI_HDR] = hdr

    # Card comment line 2: "File N  MM/DD/YYYY" -> label (still <= 32 bytes)
    b[0x20:0x40] = label.encode()[:31].ljust(32, b"\0")

    # GameStat: party_continue = 1 (bit 6 of the 0x10E flags byte)
    b[STAT + 0x10E] |= 0x40
    struct.pack_into(">Q", b, STAT + 0x08, struct.unpack_from(">Q", b, STAT + 0x08)[0] + box)

    s = SYS
    b[s + 0x04] = turn
    b[s + 0x05] = max_turn
    # save_mode = 1 (never autosave) so the scenario can be replayed
    w = struct.unpack_from(">H", b, s + 0x02)[0]
    w = (w & ~0x0180) | (1 << 7)
    struct.pack_into(">H", b, s + 0x02, w)
    b[s + 0x09] = 0          # last5_effect
    b[s + 0x0A] = 0          # player_curr
    b[s + 0x3A + 1] &= ~0x05 # clear flags 0:8 (last5 done) and 0:10 (final turn)
    b[s + 0x4A] |= 0x07      # 1:0 board init, 1:1 started, 1:2 after minigame
    b[s + 0x6A:s + 0x6A + 36] = bytes(36)  # DX per-player dice flags

    if board is not None:
        if fresh:
            # Mirror BoardSaveInit; BoardSpaceInit/BoardStartExec fill the rest
            star_pos, star_flag, star_total, block_pos = 0, 0, 1, 0
        b[s + 0x06] = star_flag
        b[s + 0x07] = star_total
        b[s + 0x08] = (star_pos << 5) | (board & 0x1F)
        struct.pack_into(">h", b, s + 0x0E, block_pos)
        b[s + 0x10:s + 0x30] = bytes(32)       # board_data
        b[s + 0x31] = 0                        # bowser_loss/event
        b[s + 0x32] = 1                        # lucky_value
        struct.pack_into(">HhH", b, s + 0x34, 0, 0, 0)  # mg_next, mg_type, unk_38
    if board is not None and fresh:
        # BoardObjectSetup's first-entry path
        b[s + 0x4A] &= ~0xFF                   # 1:0-1:7
        b[s + 0x4B] &= ~0x13                   # 1:8, 1:9, 1:12
        b[s + 0x5A] &= ~0x3F                   # 2:0-2:5

    for i, (human, items) in enumerate(players):
        p = PLY + i * 0x30
        c = coins[i] if isinstance(coins, (list, tuple)) else coins
        w = struct.unpack_from(">H", b, p)[0]
        w = (w & ~0x2000) | (0 if human else 0x2000)  # com bit
        struct.pack_into(">H", b, p, w)
        b[p + 0x05:p + 0x08] = bytes(items)
        w = struct.unpack_from(">H", b, p + 0x08)[0]
        struct.pack_into(">H", b, p + 0x08, w & 0x3FFF)  # color = 0
        struct.pack_into(">h", b, p + 0x1C, c)
        if board is not None:
            b[p] &= ~0x01; b[p + 1] &= ~0x80    # auto_size
            b[p + 1] &= ~0x40                   # draw_ticket
            b[p + 2] &= ~0x40                   # spark
            w = struct.unpack_from(">H", b, p + 0x08)[0]
            w = (w & ~(0x1000 | 0x0600 | 0x0010)) | 0x0800  # jump, size, bowser_suit off; show_next on
            struct.pack_into(">H", b, p + 0x08, w)
            struct.pack_into(">h", b, p + 0x12, 0)          # space_shock
            b[p + 0x14:p + 0x1C] = bytes(8)                 # space counters
            b[p + 0x1E:p + 0x2E] = bytes(16)                # coin stats, stars, stars_max
            if spaces:
                cur, prev = spaces[i]
                struct.pack_into(">hhh", b, p + 0x0C, cur, prev, cur)
            if stars:
                struct.pack_into(">h", b, p + 0x2A, stars[i])
                struct.pack_into(">h", b, p + 0x2C, stars[i])
                struct.pack_into(">hh", b, p + 0x20, c, c)  # coins_total, coins_max

    # Ports: human(s) on pad 0, CPUs on the remaining pads
    free = [1, 2, 3]
    for i, (human, _) in enumerate(players):
        b[PLY + i * 0x30 + 0x04] = 0 if human else free.pop(0)

    ck = (~sum(b[:SAVEDATA_END])) & 0xFFFF
    struct.pack_into(">H", b, SAVEDATA_END, ck)
    return bytes(gci)

def main(tpl_path, outdir, which=None):
    tpl = open(tpl_path, "rb").read()
    assert tpl[:6] == b"GMPE01" and len(tpl) == 0x40 + 0x4000
    out = {
        1: ("Speed Block test", {}, [
            (False, [SPEED, WARP, NONE]),
            (True,  [SPEED, SPEED, SPEED]),   # P2: the slot the bug hit
            (False, [SPEED, NONE, NONE]),
            (False, [SPEED, NONE, NONE]),
        ]),
        # Goomba's Greedy Gala, turn 5 done. Star 2 = space 27 (DX w02.bin),
        # players on blue spaces with a direct predecessor, block on blue 57.
        2: ("Warp Block test", dict(board=1, turn=5, star_pos=2, star_flag=0x05,
                                    star_total=2, block_pos=57, stars=[1, 0, 1, 0],
                                    spaces=[(18, 17), (40, 39), (63, 62), (74, 73)]), [
            (True,  [WARP, WARP, WARP]),
            (False, [WARP, WARP, WARP]),
            (False, [WARP, WARP, WARP]),
            (False, [WARP, WARP, WARP]),
        ]),
    }
    # Reversal of Fortune test (replaces the Speed Block test in slot 1): same
    # Goomba's Greedy Gala state as BOX2, P1 human with Chance Time Charms,
    # distinct coins/stars so every outcome is visible.
    out[1] = ("Fortune test", dict(board=1, turn=5, star_pos=2, star_flag=0x05,
                                   star_total=2, block_pos=57, stars=[2, 0, 3, 1],
                                   coins=[30, 80, 5, 55],
                                   spaces=[(18, 17), (40, 39), (63, 62), (74, 73)]), [
        (True,  [CHARM, CHARM, CHARM]),
        (False, [NONE, NONE, NONE]),
        (False, [NONE, NONE, NONE]),
        (False, [NONE, NONE, NONE]),
    ])
    for box, (label, opts, players) in out.items():
        if which and str(box) not in which.split(","):
            continue
        data = build(tpl, box, label, players, **opts)
        path = f"{outdir}/01-GMPE-MARIPA4BOX{box}.gci"
        open(path, "wb").write(data)
        print("wrote", path)

if __name__ == "__main__":
    main(*sys.argv[1:4])
