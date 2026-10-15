import sys, capstone, dol
ISO = sys.argv[1]; start = int(sys.argv[2], 16); n = int(sys.argv[3], 16)
secs = dol.load(ISO, 0x1e000); S = dol.syms(); rev = {a: k for k, (a, s) in S.items()}
md = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_32 | capstone.CS_MODE_BIG_ENDIAN)
code = dol.read(secs, start, n)
for i in md.disasm(code, start):
    extra = ''
    if i.mnemonic in ('bl', 'b') : 
        t = int(i.op_str, 16); extra = '  ; ' + (rev.get(t) or str(dol.symat(S, t)))
    print('%08x %s  %-8s %s%s' % (i.address, code[i.address-start:i.address-start+4].hex(), i.mnemonic, i.op_str, extra))
