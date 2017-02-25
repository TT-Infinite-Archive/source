from toontown.toonbase.ToontownSong import ToontownSong
from toontown.toonbase import TTLocalizer

THEME = 1
THEME_HALLOWEEN = 2
THEME_CHRISTMAS = 3
CREATE_A_TOON = 4
TC_NBR = 5
TC_SZ = 6
TC_ACT = 7
DD_NBR = 8
DD_SZ = 9
DD_ACT = 10
DG_NBR = 11
DG_SZ = 12
MM_NBR = 13
MM_SZ = 14
MM_ACT = 15
TB_NBR = 16
TB_SZ = 17
TB_ACT = 18
DL_NBR = 19
DL_SZ = 20
DL_ACT = 21
GS_SZ = 22
GS_KART_SHOP = 23
GS_RACE_CC = 24
GS_RACE_RR = 25
GS_RACE_SS = 26
OZ_SZ = 27
GZ_SZ = 28
GZ_PLAY_GOLF = 29
MG_CANNON = 30
MG_DIVING = 31
MG_ICE_CREAM = 32
MG_PAIRING = 33
MG_TARGET = 34
MG_TOON_TAG = 35
MG_TRAVEL = 36
MG_TUG_OF_WAR = 37
MG_TWO_D_GAME = 38
MG_VINE = 39
MG_RACE = 40
ESTATE_BGM = 41
ESTATE_INTERIOR = 42
BATTLE_INDOOR = 43
BATTLE_INDOOR_SUIT = 44
BATTLE_INDOOR_TOON = 45
ELEVATOR = 46
BATTLE_TTC = 47
BATTLE_DD = 48
BATTLE_DG = 49
BATTLE_MML = 50
BATTLE_TB = 51
BATTLE_DDL = 52
BATTLE_SUIT = 53
BATTLE_TOON = 54
BATTLE_HQ = 55
FACTORY = 56
VP_INTRO = 57
VP_ROUND_1 = 58
VP_ROUND_2 = 59
VP_BOSS = 60
CASHBOT_HQ = 61
MINT = 62
BATTLE_CASHBOT_HQ = 63
CFO_ROUND_1 = 64
CFO_ROUND_2 = 65
CFO_BOSS = 66
LAWBOT_HQ = 67
BATTLE_LAWBOT_HQ = 68
LAWBOT_JURY = 69
CJ_BOSS = 70
BOSSBOT_ENTRY_1 = 71
BOSSBOT_ENTRY_2 = 72
BOSSBOT_ENTRY_3 = 73
BOSSBOT_FACTORY_1 = 74
BOSSBOT_FACTORY_2 = 75
BOSSBOT_FACTORY_3 = 76
CEO_1 = 77
CEO_2 = 78
JELLYFISH_JAM = 79

Songs = {
    0: None,
    THEME: ToontownSong(THEME, TTLocalizer.MusicThemeSong, 'phase_3/audio/bgm/tti_theme.ogg', 90),
    THEME_HALLOWEEN: ToontownSong(THEME_HALLOWEEN, TTLocalizer.MusicHalloweenThemeSong, 'phase_3/audio/bgm/tti_theme_halloween.ogg', 63),
    THEME_CHRISTMAS: ToontownSong(THEME_CHRISTMAS, TTLocalizer.MusicChristmasThemeSong, 'phase_3/audio/bgm/tti_theme_christmas.ogg', 92),
    CREATE_A_TOON: ToontownSong(CREATE_A_TOON, TTLocalizer.MusicCreateAToon, 'phase_3/audio/bgm/create_a_toon.ogg', 175),
    TC_NBR: ToontownSong(TC_NBR, TTLocalizer.MusicTcNbrhood, 'phase_4/audio/bgm/TC_nbrhood.ogg', 58),
    TC_SZ: ToontownSong(TC_SZ, TTLocalizer.MusicTcSz, 'phase_3.5/audio/bgm/TC_SZ.ogg', 56),
    TC_ACT: ToontownSong(TC_ACT, TTLocalizer.MusicTcSzActivity, 'phase_4/audio/bgm/TC_SZ_activity.ogg', 52),
    DD_NBR: ToontownSong(DD_NBR, TTLocalizer.MusicDdNbrhood, 'phase_6/audio/bgm/DD_nbrhood.ogg', 66),
    DD_SZ: ToontownSong(DD_SZ, TTLocalizer.MusicDdSz, 'phase_6/audio/bgm/DD_SZ.ogg', 32),
    DD_ACT: ToontownSong(DD_ACT, TTLocalizer.MusicDdSzActivity, 'phase_6/audio/bgm/DD_SZ_activity.ogg', 62),
    DG_NBR: ToontownSong(DG_NBR, TTLocalizer.MusicDgNbrhood, 'phase_8/audio/bgm/DG_nbrhood.ogg', 55),
    DG_SZ: ToontownSong(DG_SZ, TTLocalizer.MusicDgSz, 'phase_8/audio/bgm/DG_SZ.ogg', 46),
    MM_NBR: ToontownSong(MM_NBR, TTLocalizer.MusicMmNbrhood, 'phase_6/audio/bgm/MM_nbrhood.ogg', 54),
    MM_SZ: ToontownSong(MM_SZ, TTLocalizer.MusicMmSz, 'phase_6/audio/bgm/MM_SZ.ogg', 75),
    MM_ACT: ToontownSong(MM_ACT, TTLocalizer.MusicMmSzActivity, 'phase_6/audio/bgm/MM_SZ_activity.ogg', 40),
    TB_NBR: ToontownSong(TB_NBR, TTLocalizer.MusicTbNbrhood, 'phase_8/audio/bgm/TB_nbrhood.ogg', 50),
    TB_SZ: ToontownSong(TB_SZ, TTLocalizer.MusicTbSz, 'phase_8/audio/bgm/TB_SZ.ogg', 54),
    TB_ACT: ToontownSong(TB_ACT, TTLocalizer.MusicTbSzActivity, 'phase_8/audio/bgm/TB_SZ_activity.ogg', 48),
    DL_NBR: ToontownSong(DL_NBR, TTLocalizer.MusicDlNbrhood, 'phase_8/audio/bgm/DL_nbrhood.ogg', 30),
    DL_SZ: ToontownSong(DL_SZ, TTLocalizer.MusicDlSz, 'phase_8/audio/bgm/DL_SZ.ogg', 32),
    DL_ACT: ToontownSong(DL_ACT, TTLocalizer.MusicDlSzActivity, 'phase_8/audio/bgm/DL_SZ_activity.ogg', 31),
    GS_SZ: ToontownSong(GS_SZ, TTLocalizer.MusicGsSz, 'phase_6/audio/bgm/GS_SZ.ogg', 59),
    GS_KART_SHOP: ToontownSong(GS_KART_SHOP, TTLocalizer.MusicGsKartshop, 'phase_6/audio/bgm/GS_KartShop.ogg', 32),
    GS_RACE_CC: ToontownSong(GS_RACE_CC, TTLocalizer.MusicGsRaceCc, 'phase_6/audio/bgm/GS_Race_CC.ogg', 58),
    GS_RACE_RR: ToontownSong(GS_RACE_RR, TTLocalizer.MusicGsRaceRr, 'phase_6/audio/bgm/GS_Race_RR.ogg', 59),
    GS_RACE_SS: ToontownSong(GS_RACE_SS, TTLocalizer.MusicGsRaceSs, 'phase_6/audio/bgm/GS_Race_SS.ogg', 60),
    OZ_SZ: ToontownSong(OZ_SZ, TTLocalizer.MusicOzSz, 'phase_6/audio/bgm/OZ_SZ.ogg', 31),
    GZ_SZ: ToontownSong(GZ_SZ, TTLocalizer.MusicGzSz, 'phase_6/audio/bgm/GZ_SZ.ogg', 59),
    GZ_PLAY_GOLF: ToontownSong(GZ_PLAY_GOLF, TTLocalizer.MusicGzPlaygolf, 'phase_6/audio/bgm/GZ_PlayGolf.ogg', 61),
    MG_CANNON: ToontownSong(MG_CANNON, TTLocalizer.MusicMgCannonGame, 'phase_4/audio/bgm/MG_cannon_game.ogg', 28),
    MG_DIVING: ToontownSong(MG_DIVING, TTLocalizer.MusicMgDiving, 'phase_4/audio/bgm/MG_Diving.ogg', 30),
    MG_ICE_CREAM: ToontownSong(MG_ICE_CREAM, TTLocalizer.MusicMgIcegame, 'phase_4/audio/bgm/MG_IceGame.ogg', 56),
    MG_PAIRING: ToontownSong(MG_PAIRING, TTLocalizer.MusicMgPairing, 'phase_4/audio/bgm/MG_Pairing.ogg', 32),
    MG_TARGET: ToontownSong(MG_TARGET, TTLocalizer.MusicMgTarget, 'phase_4/audio/bgm/MG_Target.ogg', 30),
    MG_TOON_TAG: ToontownSong(MG_TOON_TAG, TTLocalizer.MusicMgToontag, 'phase_4/audio/bgm/MG_toontag.ogg', 57),
    MG_TRAVEL: ToontownSong(MG_TRAVEL, TTLocalizer.MusicMgTravel, 'phase_4/audio/bgm/MG_Travel.ogg', 31),
    MG_TUG_OF_WAR: ToontownSong(MG_TUG_OF_WAR, TTLocalizer.MusicMgTugOWar, 'phase_4/audio/bgm/MG_tug_o_war.ogg', 28),
    MG_TWO_D_GAME: ToontownSong(MG_TWO_D_GAME, TTLocalizer.MusicMgTwodgame, 'phase_4/audio/bgm/MG_TwoDGame.ogg', 59),
    MG_VINE: ToontownSong(MG_VINE, TTLocalizer.MusicMgVine, 'phase_4/audio/bgm/MG_Vine.ogg', 32),
    MG_RACE: ToontownSong(MG_RACE, TTLocalizer.MusicMinigameRace, 'phase_4/audio/bgm/minigame_race.ogg', 77),
    ESTATE_BGM: ToontownSong(ESTATE_BGM, TTLocalizer.MusicEstateTheme, 'phase_5/audio/bgm/estate_bgm.ogg', 132),
    ESTATE_INTERIOR: ToontownSong(ESTATE_INTERIOR, TTLocalizer.MusicEstateInteriorTheme, 'phase_5/audio/bgm/estate_interior_bgm.ogg', 123),
    BATTLE_INDOOR: ToontownSong(BATTLE_INDOOR, TTLocalizer.MusicEncntrGeneralBgIndoor, 'phase_7/audio/bgm/encntr_general_bg_indoor.ogg', 31),
    BATTLE_INDOOR_SUIT: ToontownSong(BATTLE_INDOOR_SUIT, TTLocalizer.MusicEncntrGeneralSuitWinningIndoor, 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg', 36),
    BATTLE_INDOOR_TOON: ToontownSong(BATTLE_INDOOR_TOON, TTLocalizer.MusicEncntrToonWinningIndoor, 'phase_7/audio/bgm/encntr_toon_winning_indoor.ogg', 31),
    ELEVATOR: ToontownSong(ELEVATOR, TTLocalizer.MusicTtElevator, 'phase_7/audio/bgm/tt_elevator.ogg', 12),
    BATTLE_TTC: ToontownSong(BATTLE_TTC, TTLocalizer.MusicTcEncounter, 'phase_9/audio/bgm/encntr_suit_ttc.ogg', 30),
    BATTLE_DD: ToontownSong(BATTLE_DD, TTLocalizer.MusicDdEncounter, 'phase_9/audio/bgm/encntr_suit_dd.ogg', 24),
    BATTLE_DG: ToontownSong(BATTLE_DG, TTLocalizer.MusicDgEncounter, 'phase_9/audio/bgm/encntr_suit_dg.ogg', 29),
    BATTLE_MML: ToontownSong(BATTLE_MML, TTLocalizer.MusicMmEncounter, 'phase_9/audio/bgm/encntr_suit_mml.ogg', 27),
    BATTLE_TB: ToontownSong(BATTLE_TB, TTLocalizer.MusicTbEncounter, 'phase_9/audio/bgm/encntr_suit_tb.ogg', 48),
    BATTLE_DDL: ToontownSong(BATTLE_DDL, TTLocalizer.MusicDlEncounter, 'phase_9/audio/bgm/encntr_suit_ddl.ogg', 33),
    BATTLE_SUIT: ToontownSong(BATTLE_SUIT, TTLocalizer.MusicEncntrSuitWinning, 'phase_9/audio/bgm/encntr_suit_winning.ogg', 30),
    BATTLE_TOON: ToontownSong(BATTLE_TOON, TTLocalizer.MusicEncntrToonWinning, 'phase_9/audio/bgm/encntr_toon_winning.ogg', 29),
    BATTLE_HQ: ToontownSong(BATTLE_HQ, TTLocalizer.MusicSbCourtyard, 'phase_9/audio/bgm/encntr_suit_HQ_nbrhood.ogg', 42),
    FACTORY: ToontownSong(FACTORY, TTLocalizer.MusicChqFactBg, 'phase_9/audio/bgm/CHQ_FACT_bg.ogg', 48),
    VP_INTRO: ToontownSong(VP_INTRO, TTLocalizer.MusicSbBossIntro, 'phase_9/audio/bgm/VP_intro_cutscene.ogg', 46),
    VP_ROUND_1: ToontownSong(VP_ROUND_1, TTLocalizer.MusicSbBossBattle1, 'phase_9/audio/bgm/VP_round_1.ogg', 32),
    VP_ROUND_2: ToontownSong(VP_ROUND_2, TTLocalizer.MusicSbBossBattle2, 'phase_9/audio/bgm/VP_round_2.ogg', 32),
    VP_BOSS: ToontownSong(VP_BOSS, TTLocalizer.MusicSbBossBattle3, 'phase_9/audio/bgm/encntr_vp_boss.ogg', 36),
    CASHBOT_HQ: ToontownSong(CASHBOT_HQ, TTLocalizer.MusicCbCourtyard, 'phase_9/audio/bgm/CBHQ_nbrhood.ogg', 48),
    MINT: ToontownSong(MINT, TTLocalizer.MusicCbMint, 'phase_9/audio/bgm/CBHQ_Mint_bg.ogg', 34),
    BATTLE_CASHBOT_HQ: ToontownSong(BATTLE_CASHBOT_HQ, TTLocalizer.MusicCbSSEncounter, 'phase_9/audio/bgm/CB_courtyard_encntr.ogg', 28),
    CFO_ROUND_1: ToontownSong(CFO_ROUND_1, TTLocalizer.MusicCfoBattle1, 'phase_9/audio/bgm/CFO_round_1.ogg', 34),
    CFO_ROUND_2: ToontownSong(CFO_ROUND_2, TTLocalizer.MusicCfoBattle2, 'phase_9/audio/bgm/CFO_round_2.ogg', 30),
    CFO_BOSS: ToontownSong(CFO_BOSS, TTLocalizer.MusicCfoBattle3, 'phase_9/audio/bgm/encntr_cfo_boss.ogg', 66),
    LAWBOT_HQ: ToontownSong(LAWBOT_HQ, TTLocalizer.MusicLbCourtyard, 'phase_11/audio/bgm/LB_courtyard.ogg', 32),
    BATTLE_LAWBOT_HQ: ToontownSong(BATTLE_LAWBOT_HQ, TTLocalizer.MusicLbCourtyardEncounter, 'phase_11/audio/bgm/LB_courtyard_encntr.ogg', 54),
    LAWBOT_JURY: ToontownSong(LAWBOT_JURY, TTLocalizer.MusicLbJurybg, 'phase_11/audio/bgm/LB_juryBG.ogg', 29),
    CJ_BOSS: ToontownSong(CJ_BOSS, TTLocalizer.MusicLbCjFinale, 'phase_11/audio/bgm/encntr_cj_boss.ogg', 35),
    BOSSBOT_ENTRY_1: ToontownSong(BOSSBOT_ENTRY_1, TTLocalizer.MusicBossbotEntryV1, 'phase_12/audio/bgm/Bossbot_Entry_v1.ogg', 30),
    BOSSBOT_ENTRY_2: ToontownSong(BOSSBOT_ENTRY_2, TTLocalizer.MusicBossbotEntryV2, 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg', 30),
    BOSSBOT_ENTRY_3: ToontownSong(BOSSBOT_ENTRY_3, TTLocalizer.MusicBossbotEntryV3, 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg', 29),
    BOSSBOT_FACTORY_1: ToontownSong(BOSSBOT_FACTORY_1, TTLocalizer.MusicBossbotFactoryV1, 'phase_12/audio/bgm/Bossbot_Factory_v1.ogg', 30),
    BOSSBOT_FACTORY_2: ToontownSong(BOSSBOT_FACTORY_2, TTLocalizer.MusicBossbotFactoryV2, 'phase_12/audio/bgm/Bossbot_Factory_v2.ogg', 30),
    BOSSBOT_FACTORY_3: ToontownSong(BOSSBOT_FACTORY_3, TTLocalizer.MusicBossbotFactoryV3, 'phase_12/audio/bgm/Bossbot_Factory_v3.ogg', 30),
    CEO_1: ToontownSong(CEO_1, TTLocalizer.MusicBossbotCeoV1, 'phase_12/audio/bgm/BossBot_CEO_v1.ogg', 30),
    CEO_2: ToontownSong(CEO_2, TTLocalizer.MusicBossbotCeoV2, 'phase_12/audio/bgm/BossBot_CEO_v2.ogg', 30),
    JELLYFISH_JAM: ToontownSong(JELLYFISH_JAM, TTLocalizer.JellyfishJam, 'phase_13/audio/bgm/party_jellyfish_jam.ogg', 279),
}


