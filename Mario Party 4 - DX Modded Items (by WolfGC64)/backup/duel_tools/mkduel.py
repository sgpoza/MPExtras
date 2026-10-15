"""Build the duel Gecko codes (C2 hooks + compiled blob) and patch them into DX's code list in main.dol."""
import struct, sys
sys.path.insert(0, '../tools')
import ppcasm

def elf_text_and_syms(fn):
    d = open(fn, 'rb').read()
    shoff, = struct.unpack_from('>I', d, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from('>HHH', d, 0x2E)
    secs = [struct.unpack_from('>IIIIIIIIII', d, shoff + i * shentsize) for i in range(shnum)]
    sn = secs[shstrndx]
    def nm(o, base): return d[base + o:d.index(b'\0', base + o)].decode()
    byname = {nm(s[0], sn[4]): s for s in secs}
    for bad in ('.rodata', '.data', '.rela.text'):
        assert bad not in byname or byname[bad][5] == 0, bad
    t = byname['.text']
    assert t[3] == 0
    code = d[t[4]:t[4] + t[5]]
    sym = byname['.symtab']; st = secs[sym[6]]
    syms = {}
    for i in range(sym[5] // 16):
        n, v, sz, info, oth, shn = struct.unpack_from('>IIIBBH', d, sym[4] + 16 * i)
        if n and (info & 0xf) == 2: syms[nm(n, st[4])] = v
    return code, syms

def words(b): return list(struct.unpack('>%dI' % (len(b) // 4), b))

def c2(addr, body):
    """body: list of words WITHOUT the final 0 slot; pads with nop so the slot is last."""
    body = list(body)
    if len(body) % 2 == 0: body.append(0x60000000)
    body.append(0)
    return [0xC2000000 | (addr & 0x01FFFFFF), len(body) // 2] + body

def build(elf):
    code, syms = elf_text_and_syms(elf)
    blob = words(code)
    # DX's list ends with unbalanced if-blocks (4 left open); reset all code-execution status first
    out = [0xE0000000, 0x80008000]
    # --- Hook B: landing (BoardPlayerTurnMoveExec, before BoardSpaceBlockExec); carries the blob
    hdr_b = len(out)
    body_start = hdr_b + 2                     # word index of body start
    blob_start = body_start + 1                # after the leading 'b stub'
    stub_start = blob_start + len(blob)
    def fn(name): return (blob_start + syms[name] // 4) * 4   # byte position in image
    stub = ppcasm.assemble("""
        lha r4, 8(r1)
        mr r3, r31
        bl T
        mr r3, r31
    """, syms={'T': fn('duel_land') - stub_start * 4})
    lead = [0x48000000 | ((len(blob) + 1) * 4 & 0x3FFFFFC)]  # b stub
    out += c2(0x800649BC, lead + blob + stub)
    assert out[body_start] == lead[0]
    # --- Hook C: Last5Main, r3 = host portrait
    def add(addr, src, callee=None, call_index=None):
        base = len(out) + 2
        pre = ppcasm.expand(src.splitlines())
        # find position of 'bl T' (instruction index) to compute the relative target
        idx = [i for i, l in enumerate([x for x in pre if not x.endswith(':')]) if l.startswith('bl T')]
        s = {}
        if callee:
            assert len(idx) == 1
            s['T'] = fn(callee) - (base + idx[0]) * 4 + idx[0] * 4
        w = ppcasm.assemble(src, syms=s)
        out.extend(c2(addr, w))
    add(0x800AA928, """
        stwu r1, -0x10(r1)
        stw r3, 8(r1)
        bl T
        lwz r3, 8(r1)
        addi r1, r1, 0x10
        mr r5, r3
    """, 'duel_last5')
    # --- Hook D: BoardStartCheck -> 1 while a duel is pending
    add(0x8005CB48, """
        lis r12, 0x8019
        lbz r12, -0x258(r12)
        cmpwi r12, 0
        beq L
        li r3, 1
        blr
    L:
        stwu r1, -0x10(r1)
    """)
    # --- Hook E: ExecTurnStart (r31 = player) -> duel result + space event, then ZoomRestore/return 1
    add(0x8005C844, """
        mr r3, r31
        bl T
        cmpwi r3, 0
        beq L
        lis r12, 0x8005
        ori r12, r12, 0xCA60
        mtctr r12
        bctr
    L:
        lis r3, 1
    """, 'duel_resume')
    # --- Hook F: BoardObjectSetup before the flag 1:0 check
    add(0x8005B16C, """
        bl T
        lis r3, 1
    """, 'duel_fixflag')
    return out, syms, len(blob)

if __name__ == '__main__':
    out, syms, nblob = build(sys.argv[1])
    print('codes words', len(out), 'bytes', len(out) * 4, 'blob bytes', nblob * 4)
    open(sys.argv[2], 'wb').write(struct.pack('>%dI' % len(out), *out))
