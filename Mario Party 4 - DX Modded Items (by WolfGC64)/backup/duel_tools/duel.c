/* Last 5 Turns Duels for MP4 DX (GMPE01_01).
 * Runs from inside DX's GeckoLoader code list, so it must be position independent:
 * no globals, no literals in .rodata (floats come from fb()), no jump tables.
 * Game functions are called through absolute addresses (lis/ori/mtctr/bctrl). */
typedef signed char s8;
typedef unsigned char u8;
typedef short s16;
typedef unsigned short u16;
typedef int s32;
typedef unsigned int u32;
typedef struct { float x, y, z; } Vec;

#define FN(addr, ret, args) ((ret(*) args)(addr))
#define _CheckFlag              FN(0x80058010, s32, (u32))
#define _SetFlag                FN(0x800580B0, void, (u32))
#define _ClearFlag              FN(0x80058154, void, (u32))
#define HuPrcVSleep             FN(0x8000CF8C, void, (void))
#define HuPrcSleep              FN(0x8000CF0C, void, (s32))
#define HuAudFXPlay             FN(0x80032A94, s32, (s32))
#define HuAudFXAllStop          FN(0x80032BF0, void, (void))
#define WipeCreate              FN(0x800414AC, void, (s16, s16, s16))
#define WipeColorSet            FN(0x800415D8, void, (u8, u8, u8))
#define WipeStatGet             FN(0x80041600, s32, (void))
#define MessData_MesPtrGet      FN(0x800483A0, void *, (void *, u32))
#define HuAR_DVDtoARAM          FN(0x80048F4C, s32, (u32))
#define HuARDMACheck            FN(0x80049488, s32, (void))
#define BoardNextOvlSet         FN(0x8005CA84, void, (s32))
#define BoardCameraViewSet      FN(0x8005D284, void, (s32))
#define BoardCameraMoveSet      FN(0x8005D7B4, void, (s32))
#define BoardCameraTargetPlayerSet FN(0x8005D834, void, (s32))
#define BoardCameraMotionWait   FN(0x8005E0C0, void, (void))
#define BoardRandMod            FN(0x8005FB40, u32, (u32))
#define BoardPlayerGetCharMess  FN(0x80061FDC, s32, (s32))
#define BoardPlayerPosGet       FN(0x8006310C, void, (s32, Vec *))
#define BoardPlayerMotionEndWait FN(0x800638C4, void, (s32))
#define BoardPlayerMotionShiftSet FN(0x80063A1C, void, (s32, s32, float, float, u32))
#define BoardPlayerCoinsGet     FN(0x80063EC0, s32, (s32))
#define BoardPlayerCoinsAdd     FN(0x80063EEC, void, (s32, s32))
#define BoardPlayerStarsAdd     FN(0x80063F88, void, (s32, s32))
#define BoardPlayerIdleSet      FN(0x80067B98, void, (s32))
#define BoardPlayerMotBlendSet  FN(0x80067C90, void, (s32, s16, s16))
#define BoardPlayerMotBlendCheck FN(0x8006874C, s32, (s32))
#define BoardWinChoiceGet       FN(0x80070378, s32, (void))
#define BoardWinCreateChoice    FN(0x80070390, void, (s32, u32, s32, s32))
#define BoardWinCreate          FN(0x80070530, void, (s32, u32, s32))
#define BoardWinInsertMesSet    FN(0x800706D0, void, (u32, s32))
#define BoardWinWait            FN(0x800706E8, void, (void))
#define BoardWinKill            FN(0x80070738, void, (void))
#define BoardWinAttrSet         FN(0x80070770, void, (s32))
#define BoardWinChoiceDisable   FN(0x80070800, void, (s32))
#define BoardMusStartBoard      FN(0x80070D84, void, (void))
#define BoardMusStart           FN(0x80070DEC, void, (s32, s32, s8, u16))
#define BoardAudSeqFadeOut      FN(0x80070EE8, void, (s32, u16))
#define BoardAudSeqPause        FN(0x80071034, void, (s32, s32, u16))
#define BoardComKeySetUp        FN(0x80071388, void, (void))
#define BoardSpaceLandExec      FN(0x80075AF0, void, (s32, s32))
#define BoardSpaceBlockExec     FN(0x80076208, void, (s32, s32))
#define BoardCoinChgCreateRaw   FN(0x8007FE70, u32, (Vec *, s32))
#define BoardCoinChgKillCheck   FN(0x80080058, s32, (s32))
#define BoardStarGive           FN(0x80085230, void, (s32, Vec *))
#define BoardStatusShowSetAll   FN(0x800884F4, void, (s32))

#define FLAG(g, i) (((g) << 16) | (i))
#define MSG(b, i) (((b) << 16) | (i))
#define BANK 58
#define NOINS 0xFFFFFFFFu

#define SWITCH   (*(volatile u8 *)0x801D3F70)          /* set to 1 every frame by the INI Gecko code */
#define MESSDATA (*(void *volatile *)0x801D3DDC)
#define GWSYS    ((volatile u8 *)0x8018FCF8)
#define GWPLY(i) ((volatile u8 *)(0x8018FC38 + (i) * 0x30))
#define CFG(i)   ((volatile s16 *)(0x8018FC10 + (i) * 10))  /* character, pad_idx, diff, group, iscom */

/* Duel state: GWSystem+0xB0..0xD3 (saved with the game, survives the minigame) */
#define ST       ((volatile u8 *)0x8018FDA8)
#define ST_PENDING 0x00
#define ST_CHAL    0x01
#define ST_RIVAL   0x02
#define ST_BET     0x03
#define ST_STAKEC  0x04 /* s16 */
#define ST_STAKER  0x06 /* s16 */
#define ST_SPACE   0x08 /* s16 */
#define ST_MG      0x0A
#define ST_PERM    0x0C /* u8[4] */
#define ST_GROUP   0x10 /* u8[4] */
#define ST_STR(n)  ((volatile char *)(ST + 0x14 + (n) * 4))
#define ST16(o)  (*(volatile s16 *)(ST + (o)))

enum { BET_COINS, BET_STAR40, BET_STAR };

static float fb(u32 bits)
{
    volatile union { u32 u; float f; } v;
    v.u = bits;
    return v.f;
}
#define F0    0x00000000u
#define F4    0x40800000u
#define F10   0x41200000u
#define F12   0x41400000u
#define F120  0x42F00000u
#define F250  0x437A0000u

static s32 ply_com(s32 p) { return (GWPLY(p)[0] >> 5) & 1; }
static s32 ply_diff(s32 p) { return GWPLY(p)[0] >> 6; }
static s32 ply_team(s32 p) { return GWPLY(p)[2] >> 7; }
static s32 ply_space(s32 p) { return *(volatile s16 *)(GWPLY(p) + 0x0C); }
static s32 ply_stars(s32 p) { return *(volatile s16 *)(GWPLY(p) + 0x2A); }
static volatile s16 *ply_coinwin(s32 p) { return (volatile s16 *)(GWPLY(p) + 0x28); }
static s32 sys_board(void) { return GWSYS[8] & 0x1F; }
static u32 charmess(s32 p) { return (u32)BoardPlayerGetCharMess(p); }
static s32 imin(s32 a, s32 b) { return a < b ? a : b; }

static u32 numstr(s32 slot, s32 v)
{
    volatile char *b = ST_STR(slot);
    char t[4];
    s32 n = 0, i;
    if (v < 0) v = 0;
    if (v > 999) v = 999;
    do {
        t[n++] = '0' + v % 10;
        v /= 10;
    } while (v);
    for (i = 0; i < n; i++) b[i] = t[n - 1 - i];
    b[n] = 0;
    return (u32)b;
}

static void ins4(u32 a, u32 b, u32 c, u32 d)
{
    if (a != NOINS) BoardWinInsertMesSet(a, 0);
    if (b != NOINS) BoardWinInsertMesSet(b, 1);
    if (c != NOINS) BoardWinInsertMesSet(c, 2);
    if (d != NOINS) BoardWinInsertMesSet(d, 3);
}

/* Bob-omb (portrait 1) talks */
static void say(s32 idx, u32 a, u32 b, u32 c, u32 d)
{
    BoardWinCreate(2, MSG(BANK, idx), 1);
    ins4(a, b, c, d);
    BoardWinWait();
    BoardWinKill();
}

/* Menu; cpu_pick >= 0 makes the CPU (player_curr) take that option */
static s32 menu(s32 idx, u32 disabled, s32 allow_b, s32 cpu_pick, u32 a, u32 b, u32 c, u32 d)
{
    s32 i, r;
    BoardWinCreateChoice(1, MSG(BANK, idx), 1, cpu_pick >= 0 ? cpu_pick : 0);
    ins4(a, b, c, d);
    for (i = 0; i < 8; i++) {
        if (disabled & (1u << i)) BoardWinChoiceDisable(i);
    }
    if (!allow_b || cpu_pick >= 0) BoardWinAttrSet(0x10);
    if (cpu_pick >= 0) BoardComKeySetUp();
    BoardWinWait();
    r = BoardWinChoiceGet();
    BoardWinKill();
    return r;
}

static void face_camera(s32 p)
{
    BoardPlayerMotBlendSet(p, 0, 15);
    while (!BoardPlayerMotBlendCheck(p)) HuPrcVSleep();
}

static s16 bomb_create(s32 p)
{
    /* Bob-omb is shown only as the window portrait: its model (bguest.bin #38) clipped the floor */
    HuAudFXPlay(0x34A);
    return -1;
}

static void bomb_kill(s16 mdl)
{
    (void)mdl;
}

static void coin_transfer(s32 from, s32 to, s32 n)
{
    Vec pos;
    s32 c1 = -1, c2 = -1, i, wait;
    if (n <= 0) return;
    if (n <= 99) {
        BoardPlayerPosGet(from, &pos);
        pos.y = pos.y + fb(F250);
        c1 = (s8)(u8)BoardCoinChgCreateRaw(&pos, -n);
        BoardPlayerPosGet(to, &pos);
        pos.y = pos.y + fb(F250);
        c2 = (s8)(u8)BoardCoinChgCreateRaw(&pos, n);
    }
    BoardPlayerMotionShiftSet(from, 13, fb(F0), fb(F4), 0);
    BoardPlayerMotionShiftSet(to, 12, fb(F0), fb(F4), 0);
    wait = n >= 20 ? 3 : 6;
    for (i = 0; i < n; i++) {
        BoardPlayerCoinsAdd(from, -1);
        BoardPlayerCoinsAdd(to, 1);
        HuAudFXPlay(14);
        HuPrcSleep(wait);
    }
    HuAudFXPlay(15);
    if (c1 >= 0) while (!BoardCoinChgKillCheck(c1)) HuPrcVSleep();
    if (c2 >= 0) while (!BoardCoinChgKillCheck(c2)) HuPrcVSleep();
    BoardPlayerMotionEndWait(from);
    BoardPlayerMotionEndWait(to);
    BoardPlayerIdleSet(from);
    BoardPlayerIdleSet(to);
}

static void star_transfer(s32 from, s32 to)
{
    Vec pos;
    if (ply_stars(from) <= 0) return;
    BoardPlayerStarsAdd(from, -1);
    HuAudFXPlay(15);
    if (sys_board() >= 7) {
        BoardPlayerStarsAdd(to, 1);
        return;
    }
    BoardPlayerPosGet(from, &pos);
    BoardStarGive(to, &pos);
    BoardPlayerIdleSet(to);
}

/* winner < 0: tie */
static void payout(s32 winner)
{
    s32 chal = ST[ST_CHAL], rival = ST[ST_RIVAL], loser, n;
    if (winner < 0) {
        say(13, NOINS, NOINS, NOINS, NOINS);
        return;
    }
    loser = winner == chal ? rival : chal;
    say(12, charmess(winner), NOINS, NOINS, NOINS);
    switch (ST[ST_BET]) {
        case BET_COINS:
            n = imin(winner == chal ? ST16(ST_STAKER) : ST16(ST_STAKEC), BoardPlayerCoinsGet(loser));
            say(14, charmess(winner), charmess(loser), numstr(2, n), NOINS);
            coin_transfer(loser, winner, n);
            break;
        case BET_STAR40:
            if (winner == chal) {
                say(15, charmess(winner), charmess(loser), NOINS, NOINS);
                star_transfer(loser, winner);
            } else {
                n = imin(40, BoardPlayerCoinsGet(loser));
                say(14, charmess(winner), charmess(loser), numstr(2, n), NOINS);
                coin_transfer(loser, winner, n);
            }
            break;
        default:
            say(15, charmess(winner), charmess(loser), NOINS, NOINS);
            star_transfer(loser, winner);
            break;
    }
}

static void music_end(void)
{
    BoardAudSeqFadeOut(1, 1000);
    BoardAudSeqPause(0, 0, 1000);
}

/* Hook at BoardPlayerTurnMoveExec, right before BoardSpaceBlockExec. Returns normally
 * unless a minigame is launched (then the board is killed and this never returns). */
void duel_land(s32 chal, s32 space)
{
    s32 rivals[3], nriv = 0, rival, i, r, cc, rc, cs, rs, bet, sel, x, mga, mgb, mg;
    u32 dis, half, all;
    s16 bomb;
    s32 cpu = ply_com(chal);

    if (SWITCH != 1 || ST[ST_PENDING]) return;
    if ((s32)GWSYS[5] - (s32)GWSYS[4] >= 5) return;            /* Last 5 Turns only */
    if (_CheckFlag(FLAG(1, 11))) return;                         /* tutorial */
    if (!MESSDATA || !MessData_MesPtrGet(MESSDATA, MSG(BANK, 26))) return; /* text missing */
    for (i = 0; i < 4; i++) {
        if (i == chal || ply_space(i) != space) continue;
        if ((GWSYS[0] & 0x40) && ply_team(i) == ply_team(chal)) continue;
        rivals[nriv++] = i;
    }
    if (nriv == 0) return;

    BoardCameraViewSet(2);
    face_camera(chal);
    BoardCameraMotionWait();
    BoardAudSeqPause(0, 1, 500);
    BoardMusStart(1, 4, 0x7F, 0);
    bomb = bomb_create(chal);

    rival = rivals[0];
    if (nriv > 1) {
        r = -1;
        if (cpu) {
            s32 best = 0;
            for (i = 1; i < nriv; i++) {
                if (ply_stars(rivals[i]) > ply_stars(rivals[best])
                    || (ply_stars(rivals[i]) == ply_stars(rivals[best])
                        && BoardPlayerCoinsGet(rivals[i]) > BoardPlayerCoinsGet(rivals[best])))
                    best = i;
            }
            r = best;
        }
        r = menu(nriv == 2 ? 3 : 4, 0, 0, r, charmess(rivals[0]), charmess(rivals[1]),
                 nriv > 2 ? charmess(rivals[2]) : NOINS, NOINS);
        if (r < 0 || r >= nriv) r = 0;
        rival = rivals[r];
    }
    say(0, charmess(chal), charmess(rival), NOINS, NOINS);

    cc = BoardPlayerCoinsGet(chal);
    rc = BoardPlayerCoinsGet(rival);
    cs = ply_stars(chal);
    rs = ply_stars(rival);
    dis = 0;
    if (cc <= 0 || rc <= 0) dis |= 1 << BET_COINS;
    if (cc < 40 || rs < 1) dis |= 1 << BET_STAR40;
    if (cs < 1 || rs < 1) dis |= 1 << BET_STAR;
    if (dis == 7) {
        say(9, NOINS, NOINS, NOINS, NOINS);
        bomb_kill(bomb);
        music_end();
        return;
    }

    ST16(ST_STAKEC) = 0;
    ST16(ST_STAKER) = 0;
    half = numstr(0, (rc + 1) / 2);
    all = numstr(1, rc);
    for (;;) {
        s32 pick = -1;
        if (cpu) {
            if (!(dis & (1 << BET_STAR)) && cs <= rs) pick = BET_STAR;
            else if (!(dis & (1 << BET_STAR40)) && cc >= 60) pick = BET_STAR40;
            else if (!(dis & (1 << BET_COINS))) pick = BET_COINS;
            else if (!(dis & (1 << BET_STAR))) pick = BET_STAR;
            else pick = BET_STAR40;
        }
        bet = menu(1, dis, 0, pick, NOINS, NOINS, NOINS, NOINS);
        if (bet < 0 || bet > 2 || (dis & (1u << bet))) continue;
        if (bet != BET_COINS) break;
        pick = -1;
        if (cpu) pick = cc >= rc ? 3 : (cc >= 20 ? 1 : 0);
        sel = menu(2, 0, 1, pick, charmess(rival), NOINS, half, all);
        if (sel < 0 || sel > 3) continue; /* B: back to the bet menu */
        x = sel == 0 ? 10 : sel == 1 ? 20 : sel == 2 ? (rc + 1) / 2 : rc;
        ST16(ST_STAKEC) = imin(x, cc);
        ST16(ST_STAKER) = imin(x, rc);
        break;
    }
    ST[ST_CHAL] = chal;
    ST[ST_RIVAL] = rival;
    ST[ST_BET] = bet;
    ST16(ST_SPACE) = space;
    if (bet == BET_COINS)
        say(6, charmess(chal), charmess(rival), numstr(2, ST16(ST_STAKEC)), numstr(3, ST16(ST_STAKER)));
    else
        say(bet == BET_STAR40 ? 7 : 8, charmess(chal), charmess(rival), NOINS, NOINS);

    /* Both CPUs and "show COM mini-games" off: simulate (difficulty shifts the odds) */
    if (cpu && ply_com(rival) && !(GWSYS[2] & 0x20)) {
        s32 odds = 50 + 10 * (ply_diff(chal) - ply_diff(rival));
        say(11, NOINS, NOINS, NOINS, NOINS);
        payout((s32)BoardRandMod(100) < odds ? chal : rival);
        say(16, NOINS, NOINS, NOINS, NOINS);
        bomb_kill(bomb);
        music_end();
        return;
    }

    /* The challenger picks one of two random duel games (5 Story games, Bowser Wrestling, Panels of Doom) */
    mga = BoardRandMod(7);
    mgb = BoardRandMod(6);
    if (mgb >= mga) mgb++;
    r = menu(5, 0, 0, cpu ? (s32)BoardRandMod(2) : -1, MSG(BANK, 20 + mga), MSG(BANK, 20 + mgb), NOINS, NOINS);
    mg = r == 1 ? mgb : mga;
    ST[ST_MG] = mg;
    say(10, NOINS, NOINS, MSG(BANK, 20 + mg), NOINS);

    /* Leave the board like the Bowser Space mini-games do */
    BoardAudSeqFadeOut(1, 1000);
    _SetFlag(FLAG(1, 14));
    WipeColorSet(255, 255, 255);
    WipeCreate(2, 0, -1);
    while (WipeStatGet()) HuPrcVSleep();
    HuAudFXAllStop();
    _SetFlag(FLAG(1, 28));
    bomb_kill(bomb);

    /* Duelists into config slots 0/1 (sides 0/1), the others into 2/3 */
    {
        s16 save[4][5];
        s32 perm[4], k = 2, j;
        perm[0] = chal;
        perm[1] = rival;
        for (i = 0; i < 4; i++) {
            if (i != chal && i != rival) perm[k++] = i;
        }
        for (i = 0; i < 4; i++) {
            ST[ST_PERM + i] = perm[i];
            ST[ST_GROUP + i] = CFG(i)[3];
            for (j = 0; j < 5; j++) save[i][j] = CFG(i)[j];
        }
        for (i = 0; i < 4; i++) {
            for (j = 0; j < 5; j++) CFG(i)[j] = save[perm[i]][j];
            CFG(i)[3] = i;
            *ply_coinwin(i) = 0;
        }
    }
    *(volatile u16 *)(GWSYS + 0x34) = mg < 5 ? 44 + mg : 51 + mg; /* mg_next: mgInfoTbl index */
    _ClearFlag(FLAG(1, 0)); /* normal 2P versus in m457/m458; resultDll returns at once; restored by duel_fixflag */
    ST[ST_PENDING] = 1;
    BoardNextOvlSet(3); /* instdll */
    for (;;) HuPrcVSleep();
}

/* Hook at BoardObjectSetup before its flag 1:0 check */
void duel_fixflag(void)
{
    if (ST[ST_PENDING] && !_CheckFlag(FLAG(1, 0))) {
        _SetFlag(FLAG(1, 0));
        HuAR_DVDtoARAM(0x70000); /* DATADIR_BOARD, as resultDll does for board games */
        while (HuARDMACheck()) {}
    }
}

/* Hook in ExecTurnStart; returns 1 when it handled the turn (duel result + space event) */
s32 duel_resume(s32 player)
{
    s32 chal, rival, space, i, j, w0, w1, winner;
    s16 save[4][5];
    s16 bomb;

    if (!ST[ST_PENDING]) return 0;
    ST[ST_PENDING] = 0;
    chal = ST[ST_CHAL];
    rival = ST[ST_RIVAL];
    space = ST16(ST_SPACE);

    for (i = 0; i < 4; i++) {
        for (j = 0; j < 5; j++) save[i][j] = CFG(i)[j];
    }
    for (i = 0; i < 4; i++) {
        s32 p = ST[ST_PERM + i] & 3;
        for (j = 0; j < 5; j++) CFG(p)[j] = save[i][j];
    }
    for (i = 0; i < 4; i++) CFG(i)[3] = ST[ST_GROUP + i];
    w0 = *ply_coinwin(0);
    w1 = *ply_coinwin(1);
    for (i = 0; i < 4; i++) *ply_coinwin(i) = 0;
    winner = (w0 > 0 && w1 <= 0) ? chal : (w1 > 0 && w0 <= 0) ? rival : -1;

    BoardCameraMoveSet(0);
    BoardCameraTargetPlayerSet(chal);
    BoardCameraViewSet(2);
    BoardCameraMotionWait();
    BoardStatusShowSetAll(1);
    WipeCreate(1, 0, 21);
    while (WipeStatGet()) HuPrcVSleep();
    _ClearFlag(FLAG(1, 28));
    BoardCameraMoveSet(1);
    BoardMusStart(1, 4, 0x7F, 0);
    face_camera(chal);
    bomb = bomb_create(chal);
    payout(winner);
    say(16, NOINS, NOINS, NOINS, NOINS);
    bomb_kill(bomb);
    BoardAudSeqFadeOut(1, 1000);
    BoardMusStartBoard();

    /* the space's own event, as if the turn had not been interrupted */
    BoardSpaceBlockExec(chal, space);
    BoardSpaceLandExec(chal, space);
    _SetFlag(FLAG(1, 14));
    return 1;
}

/* Hook in Last5Main before the host's closing line */
void duel_last5(s32 portrait)
{
    s32 board = sys_board();
    if (SWITCH != 1 || board > 5) return;
    if (!MESSDATA || !MessData_MesPtrGet(MESSDATA, MSG(57, 2 + board))) return;
    if (!MessData_MesPtrGet(MESSDATA, MSG(BANK, 26))) return;
    BoardWinCreate(2, MSG(57, 2 + board), portrait);
    BoardWinWait();
    BoardWinKill();
}
