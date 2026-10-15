"""Tiny PowerPC assembler (subset) for Gecko C2 inserts. Labels end with ':'.
'call ADDR' expands to lis/ori r12 + mtctr + bctrl."""
import re
D = dict(addi=14, addis=15, mulli=7, lbz=34, lhz=40, lha=42, lwz=32, stb=38, sth=44, stw=36,
         stwu=37, lmw=46, stmw=47, lfs=48, stfs=52, addic_=13)
LOGI = dict(ori=24, andi_=28)
X31 = dict(add=(266, 'dab'), subf=(40, 'dab'), neg=(104, 'da'), xor=(316, 'sab'), or_=(444, 'sab'),
           extsb=(954, 'sa'))
BC = dict(beq=(12, 2), bne=(4, 2), blt=(12, 0), bge=(4, 0), bgt=(12, 1), ble=(4, 1))
def reg(s):
    s = s.strip().lower()
    assert s[0] in 'rf', s
    return int(s[1:])
def imm(s, syms):
    s = s.strip()
    return int(eval(s, {}, syms))
def expand(lines):
    out = []
    for l in lines:
        l = l.split(';')[0].strip()
        if not l: continue
        m = re.match(r'call\s+(\S+)', l)
        if m:
            out += ['lis r12, (%s)>>16' % m.group(1), 'ori r12, r12, (%s)&0xFFFF' % m.group(1), 'mtctr r12', 'bctrl']
        else: out.append(l)
    return out
def assemble(src, base=0, syms=None):
    syms = dict(syms or {})
    lines = expand(src.splitlines())
    pc = 0; ins = []
    for l in lines:
        if l.endswith(':'): syms[l[:-1]] = pc
        else: ins.append((pc, l)); pc += 4
    words = []
    for pc, l in ins:
        op, _, args = l.partition(' ')
        a = [x.strip() for x in args.split(',')] if args.strip() else []
        o = op.replace('.', '_')
        if o in ('lfs', 'stfs', 'lbz', 'lhz', 'lha', 'lwz', 'stb', 'sth', 'stw', 'stwu', 'lmw', 'stmw'):
            m = re.match(r'(.+)\((r\d+)\)', a[1]); d = imm(m.group(1), syms) & 0xFFFF
            w = D[o] << 26 | reg(a[0]) << 21 | reg(m.group(2)) << 16 | d
        elif o in ('addi', 'addis', 'mulli', 'addic_'):
            w = D[o] << 26 | reg(a[0]) << 21 | reg(a[1]) << 16 | (imm(a[2], syms) & 0xFFFF)
        elif o == 'subic_':
            w = 13 << 26 | reg(a[0]) << 21 | reg(a[1]) << 16 | (-imm(a[2], syms) & 0xFFFF)
        elif o == 'li': w = 14 << 26 | reg(a[0]) << 21 | (imm(a[1], syms) & 0xFFFF)
        elif o == 'lis': w = 15 << 26 | reg(a[0]) << 21 | (imm(a[1], syms) & 0xFFFF)
        elif o in LOGI: w = LOGI[o] << 26 | reg(a[1]) << 21 | reg(a[0]) << 16 | (imm(a[2], syms) & 0xFFFF)
        elif o == 'mr': w = 31 << 26 | reg(a[1]) << 21 | reg(a[0]) << 16 | reg(a[1]) << 11 | 444 << 1
        elif o in X31 or o + '_' in X31:
            xo, f = X31.get(o) or X31[o + '_']
            if f == 'dab': w = reg(a[0]) << 21 | reg(a[1]) << 16 | reg(a[2]) << 11
            elif f == 'da': w = reg(a[0]) << 21 | reg(a[1]) << 16
            elif f == 'sab': w = reg(a[1]) << 21 | reg(a[0]) << 16 | reg(a[2]) << 11
            elif f == 'sa': w = reg(a[1]) << 21 | reg(a[0]) << 16
            w |= 31 << 26 | xo << 1
        elif o in ('cmpwi', 'cmplwi'):
            w = (11 if o == 'cmpwi' else 10) << 26 | reg(a[0]) << 16 | (imm(a[1], syms) & 0xFFFF)
        elif o == 'cmpw': w = 31 << 26 | reg(a[0]) << 16 | reg(a[1]) << 11
        elif o == 'fadds': w = 59 << 26 | reg(a[0]) << 21 | reg(a[1]) << 16 | reg(a[2]) << 11 | 21 << 1
        elif o == 'mflr': w = 31 << 26 | reg(a[0]) << 21 | 0x100 << 11 | 339 << 1
        elif o == 'mtlr': w = 31 << 26 | reg(a[0]) << 21 | 0x100 << 11 | 467 << 1
        elif o == 'mtctr': w = 31 << 26 | reg(a[0]) << 21 | 0x120 << 11 | 467 << 1
        elif o == 'bctrl': w = 0x4E800421
        elif o == 'blr': w = 0x4E800020
        elif o == 'nop': w = 0x60000000
        elif o in ('b', 'bl'):
            d = imm(a[0], syms) - pc; w = 18 << 26 | (d & 0x3FFFFFC) | (o == 'bl')
        elif o in BC:
            bo, bi = BC[o]; d = imm(a[0], syms) - pc; assert -0x8000 <= d < 0x8000
            w = 16 << 26 | bo << 21 | bi << 16 | (d & 0xFFFC)
        else: raise ValueError(l)
        words.append(w)
    return words
def c2(addr, words):
    words = list(words)
    if len(words) % 2 == 0: words.append(0x60000000)
    words.append(0)
    out = ['C2%06X %08X' % (addr & 0x1FFFFFF, len(words) // 2)]
    for i in range(0, len(words), 2): out.append('%08X %08X' % (words[i], words[i+1]))
    return out
