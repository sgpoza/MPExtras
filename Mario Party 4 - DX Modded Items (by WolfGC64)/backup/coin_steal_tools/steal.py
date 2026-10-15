"""Last 5 Turns coin steal: Gecko code generator."""
import capstone, ppcasm
SYMS = dict(
    _CheckFlag=0x80058010, BoardCameraViewSet=0x8005D284, BoardCameraMotionWait=0x8005E0C0,
    BoardPlayerMotBlendSet=0x80067C90, BoardPlayerMotBlendCheck=0x8006874C, HuPrcVSleep=0x8000CF8C,
    HuPrcSleep=0x8000CF0C, HuAudFXPlay=0x80032A94, BoardPlayerCoinsGet=0x80063EC0,
    BoardPlayerCoinsAdd=0x80063EEC, BoardWinCreate=0x80070530, BoardWinInsertMesSet=0x800706D0,
    BoardWinWait=0x800706E8, BoardPlayerGetCharMess=0x80061FDC, BoardPlayerPosGet=0x8006310C,
    BoardCoinChgCreate=0x8007FE70, BoardCoinChgKillCheck=0x80080058, BoardPlayerMotionShiftSet=0x80063A1C,
    BoardPlayerMotionEndWait=0x800638C4, BoardPlayerIdleSet=0x80067B98,
    MessData_MesPtrGet=0x800483A0,
    MESS_BANK=57,
)
HOOK_A = 0x800648F0   # BoardPlayerTurnMoveExec: mr r3,r31 before bl BoardRollUpdateSet (movement done)
HOOK_B = 0x800649BC   # BoardPlayerTurnMoveExec: mr r3,r31 before bl BoardSpaceBlockExec
HOOK_C = 0x800AA928   # Last5Main: mr r5,r3 after BoardWinPortraitGetStar, before the closing messBase+23 window

# GWSystem+0xD4 (0x8018FDCC) u16: mover was Mega (size 2) or in the Bowser Suit
# GWSystem+0xD8 (0x8018FDD0) char[4]: stolen amount as text for the message
SRC_A = """
mulli r12, r31, 0x30
lis r11, 0x8019
addi r11, r11, -0x3C8        ; GWPlayer
add r12, r11, r12
lhz r12, 8(r12)
andi. r12, r12, 0x410        ; size == 2 (Mega) | bowser_suit
lis r11, 0x8019
sth r12, -0x234(r11)         ; 0x8018FDCC
mr r3, r31
"""

SRC_B = """
stwu r1, -0x60(r1)
mflr r0
stw r0, 0x64(r1)
stmw r24, 0x40(r1)
lis r28, 0x8019
addi r28, r28, -0x308        ; GWSystem
lhz r0, 0xD4(r28)            ; Mega/Bowser Suit already crushed them
li r3, 0
sth r3, 0xD4(r28)
cmpwi r0, 0
bne done
lbz r3, 4(r28)               ; turn
lbz r4, 5(r28)               ; max_turn
subf r4, r3, r4
cmpwi r4, 5                  ; last 5 turns: max_turn - turn < 5
bge done
lis r3, 1
addi r3, r3, 0xB             ; tutorial
call _CheckFlag
cmpwi r3, 0
bne done
lis r3, 0x801D
lwz r3, 0x3DDC(r3)           ; messDataPtr
cmpwi r3, 0
beq done
lis r4, MESS_BANK
addi r4, r4, 1
call MessData_MesPtrGet      ; text missing (not the patched ISO): do nothing
cmpwi r3, 0
beq done
lha r30, 0x68(r1)            ; landing space (caller's sp+8)
li r27, 0                    ; other player
li r26, 0                    ; camera set up
loop:
cmpw r27, r31
beq next
lis r3, 0x8019
addi r3, r3, -0x3C8
mulli r4, r27, 0x30
add r25, r3, r4
mulli r4, r31, 0x30
add r24, r3, r4
lha r0, 0xC(r25)             ; space_curr
cmpw r0, r30
bne next
lbz r0, 0(r28)
andi. r0, r0, 0x40           ; team battle: skip partner
beq noteam
lbz r0, 2(r25)
lbz r3, 2(r24)
xor r0, r0, r3
andi. r0, r0, 0x80
beq next
noteam:
cmpwi r26, 0
bne skipcam
li r26, 1
li r3, 2
call BoardCameraViewSet
mr r3, r31
li r4, 0
li r5, 15
call BoardPlayerMotBlendSet
blend:
mr r3, r31
call BoardPlayerMotBlendCheck
cmpwi r3, 0
bne blended
call HuPrcVSleep
b blend
blended:
call BoardCameraMotionWait
skipcam:
mr r3, r27
call BoardPlayerCoinsGet
mr r29, r3                   ; n = min(coins, 10)
cmpwi r29, 10
ble le10
li r29, 10
le10:
lis r25, 0x8019
addi r25, r25, -0x230        ; 0x8018FDD0 text buffer
cmpwi r29, 10
blt onedig
li r0, 0x3130                ; "10"
sth r0, 0(r25)
li r0, 0
stb r0, 2(r25)
b strdone
onedig:
addi r0, r29, 0x30
stb r0, 0(r25)
li r0, 0
stb r0, 1(r25)
strdone:
li r3, 2
lis r4, MESS_BANK
cmpwi r29, 0
bne havecoins
ori r4, r4, 1                ; message 1: victim has no coins
havecoins:
li r5, -1
call BoardWinCreate
mr r3, r31
call BoardPlayerGetCharMess
li r4, 0
call BoardWinInsertMesSet
mr r3, r27
call BoardPlayerGetCharMess
li r4, 1
call BoardWinInsertMesSet
mr r3, r25
li r4, 2
call BoardWinInsertMesSet
call BoardWinWait
cmpwi r29, 0
beq next
lis r0, 0x437A               ; 250.0f
stw r0, 0x30(r1)
lis r0, 0x4080               ; 4.0f
stw r0, 0x34(r1)
li r0, 0                     ; 0.0f
stw r0, 0x38(r1)
mr r3, r27
addi r4, r1, 8
call BoardPlayerPosGet
lfs f1, 0xC(r1)
lfs f0, 0x30(r1)
fadds f1, f1, f0
stfs f1, 0xC(r1)
addi r3, r1, 8
neg r4, r29
call BoardCoinChgCreate      ; -n over the victim
extsb r3, r3
stw r3, 0x18(r1)
mr r3, r31
addi r4, r1, 8
call BoardPlayerPosGet
lfs f1, 0xC(r1)
lfs f0, 0x30(r1)
fadds f1, f1, f0
stfs f1, 0xC(r1)
addi r3, r1, 8
mr r4, r29
call BoardCoinChgCreate      ; +n over the thief
extsb r3, r3
stw r3, 0x1C(r1)
mr r3, r27
li r4, 13                    ; lose-coins motion
lfs f1, 0x38(r1)
lfs f2, 0x34(r1)
li r5, 0
call BoardPlayerMotionShiftSet
mr r3, r31
li r4, 12                    ; gain-coins motion
lfs f1, 0x38(r1)
lfs f2, 0x34(r1)
li r5, 0
call BoardPlayerMotionShiftSet
mr r24, r29
coinloop:
mr r3, r27
li r4, -1
call BoardPlayerCoinsAdd
mr r3, r31
li r4, 1
call BoardPlayerCoinsAdd
li r3, 14
call HuAudFXPlay
li r3, 6
call HuPrcSleep
subic. r24, r24, 1
bne coinloop
li r3, 15
call HuAudFXPlay
kc1:
lwz r3, 0x18(r1)
call BoardCoinChgKillCheck
cmpwi r3, 0
bne kc2
call HuPrcVSleep
b kc1
kc2:
lwz r3, 0x1C(r1)
call BoardCoinChgKillCheck
cmpwi r3, 0
bne kcdone
call HuPrcVSleep
b kc2
kcdone:
mr r3, r31
call BoardPlayerMotionEndWait
mr r3, r31
call BoardPlayerIdleSet
mr r3, r27
call BoardPlayerMotionEndWait
mr r3, r27
call BoardPlayerIdleSet
next:
addi r27, r27, 1
cmpwi r27, 4
blt loop
done:
lmw r24, 0x40(r1)
lwz r0, 0x64(r1)
mtlr r0
addi r1, r1, 0x60
mr r3, r31
"""

# Host announces the rule in the Last Five Turns Event (bank 57, msg 2 + board, boards 0-5)
SRC_C = """
stwu r1, -0x20(r1)
mflr r0
stw r0, 0x24(r1)
stw r31, 0x1C(r1)
stw r30, 0x18(r1)
mr r31, r3                   ; host portrait
lis r30, 0x8019
lbz r30, -0x300(r30)         ; GWSystem+8: star_pos:3 | board:5
andi. r30, r30, 0x1F
cmplwi r30, 5
bgt skip
lis r3, 0x801D
lwz r3, 0x3DDC(r3)           ; messDataPtr
cmpwi r3, 0
beq skip
lis r4, MESS_BANK
addi r4, r4, 2
add r4, r4, r30
call MessData_MesPtrGet      ; text missing (not the patched ISO): skip
cmpwi r3, 0
beq skip
li r3, 2
lis r4, MESS_BANK
addi r4, r4, 2
add r4, r4, r30
mr r5, r31
call BoardWinCreate
call BoardWinWait
skip:
mr r3, r31
lwz r30, 0x18(r1)
lwz r31, 0x1C(r1)
lwz r0, 0x24(r1)
mtlr r0
addi r1, r1, 0x20
mr r5, r3
"""

def build():
    a = ppcasm.assemble(SRC_A, syms=SYMS)
    b = ppcasm.assemble(SRC_B, syms=SYMS)
    c = ppcasm.assemble(SRC_C, syms=SYMS)
    return a, b, c, ppcasm.c2(HOOK_A, a) + ppcasm.c2(HOOK_B, b) + ppcasm.c2(HOOK_C, c)

if __name__ == '__main__':
    import sys, struct
    a, b, c, lines = build()
    if 'dis' in sys.argv:
        md = capstone.Cs(capstone.CS_ARCH_PPC, capstone.CS_MODE_32 | capstone.CS_MODE_BIG_ENDIAN)
        for name, w in (('A', a), ('B', b), ('C', c)):
            print('==', name, len(w))
            code = struct.pack('>%dI' % len(w), *w)
            n = 0
            for i in md.disasm(code, 0):
                print('%04x %08x  %s %s' % (i.address, w[i.address // 4], i.mnemonic, i.op_str)); n += 1
            assert n == len(w), 'capstone stopped at %d/%d' % (n, len(w))
    else:
        print('\n'.join(lines))
