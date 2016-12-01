from toontown.toonbase import TTLocalizer


class ToontownSong:
    def __init__(self, uid, name, path, length):
        self.uid = uid
        self.name = name
        self.path = path
        self.length = length

    def getAudioSound(self):
        music = loader.loadMusic(self.path)
        return music

    def getLength(self):
        return self.length

Songs = {
    0: None,
    1: ToontownSong(1, TTLocalizer.MusicThemeSong, 'phase_3/audio/bgm/tti_theme.ogg', 90),
    2: ToontownSong(2, TTLocalizer.MusicHalloweenThemeSong, 'phase_3/audio/bgm/tti_theme_halloween.ogg', 63),
    3: ToontownSong(3, TTLocalizer.MusicChristmasThemeSong, 'phase_3/audio/bgm/tti_theme_christmas.ogg', 92),
    4: ToontownSong(4, TTLocalizer.MusicCreateAToon, 'phase_3/audio/bgm/create_a_toon.ogg', 175),
    5: ToontownSong(5, TTLocalizer.MusicTcNbrhood, 'phase_4/audio/bgm/TC_nbrhood.ogg', 58),
    6: ToontownSong(6, TTLocalizer.MusicTcSz, 'phase_4/audio/bgm/TC_SZ.ogg', 56),
    7: ToontownSong(7, TTLocalizer.MusicTcSzActivity, 'phase_4/audio/bgm/TC_SZ_activity.ogg', 52),
    8: ToontownSong(8, TTLocalizer.MusicDdNbrhood, 'phase_6/audio/bgm/DD_nbrhood.ogg', 66),
    9: ToontownSong(9, TTLocalizer.MusicDdSz, 'phase_6/audio/bgm/DD_SZ.ogg', 32),
    10: ToontownSong(10, TTLocalizer.MusicDdSzActivity, 'phase_6/audio/bgm/DD_SZ_activity.ogg', 62),
    11: ToontownSong(11, TTLocalizer.MusicDgNbrhood, 'phase_8/audio/bgm/DG_nbrhood.ogg', 55),
    12: ToontownSong(12, TTLocalizer.MusicDgSz, 'phase_8/audio/bgm/DG_SZ.ogg', 46),
    13: ToontownSong(13, TTLocalizer.MusicMmNbrhood, 'phase_6/audio/bgm/MM_nbrhood.ogg', 54),
    14: ToontownSong(14, TTLocalizer.MusicMmSz, 'phase_6/audio/bgm/MM_SZ.ogg', 75),
    15: ToontownSong(15, TTLocalizer.MusicMmSzActivity, 'phase_6/audio/bgm/MM_SZ_activity.ogg', 40),
    16: ToontownSong(16, TTLocalizer.MusicTbNbrhood, 'phase_8/audio/bgm/TB_nbrhood.ogg', 50),
    17: ToontownSong(17, TTLocalizer.MusicTbSz, 'phase_8/audio/bgm/TB_SZ.ogg', 54),
    18: ToontownSong(18, TTLocalizer.MusicTbSzActivity, 'phase_8/audio/bgm/TB_SZ_activity.ogg', 48),
    19: ToontownSong(19, TTLocalizer.MusicDlNbrhood, 'phase_8/audio/bgm/DL_nbrhood.ogg', 30),
    20: ToontownSong(20, TTLocalizer.MusicDlSz, 'phase_8/audio/bgm/DL_SZ.ogg', 32),
    21: ToontownSong(21, TTLocalizer.MusicDlSzActivity, 'phase_8/audio/bgm/DL_SZ_activity.ogg', 31),
    22: ToontownSong(22, TTLocalizer.MusicGsSz, 'phase_6/audio/bgm/GS_SZ.ogg', 59),
    23: ToontownSong(23, TTLocalizer.MusicGsKartshop, 'phase_6/audio/bgm/GS_KartShop.ogg', 32),
    24: ToontownSong(24, TTLocalizer.MusicGsRaceCc, 'phase_6/audio/bgm/GS_Race_CC.ogg', 58),
    25: ToontownSong(25, TTLocalizer.MusicGsRaceRr, 'phase_6/audio/bgm/GS_Race_RR.ogg', 59),
    26: ToontownSong(26, TTLocalizer.MusicGsRaceSs, 'phase_6/audio/bgm/GS_Race_SS.ogg', 60),
    27: ToontownSong(27, TTLocalizer.MusicOzSz, 'phase_6/audio/bgm/OZ_SZ.ogg', 31),
    28: ToontownSong(28, TTLocalizer.MusicGzSz, 'phase_6/audio/bgm/GZ_SZ.ogg', 59),
    29: ToontownSong(29, TTLocalizer.MusicGzPlaygolf, 'phase_6/audio/bgm/GZ_PlayGolf.ogg', 61),
    30: ToontownSong(30, TTLocalizer.MusicMgCannonGame, 'phase_4/audio/bgm/MG_cannon_game.ogg', 28),
    31: ToontownSong(31, TTLocalizer.MusicMgDiving, 'phase_4/audio/bgm/MG_Diving.ogg', 30),
    32: ToontownSong(32, TTLocalizer.MusicMgIcegame, 'phase_4/audio/bgm/MG_IceGame.ogg', 56),
    33: ToontownSong(33, TTLocalizer.MusicMgPairing, 'phase_4/audio/bgm/MG_Pairing.ogg', 32),
    34: ToontownSong(34, TTLocalizer.MusicMgTarget, 'phase_4/audio/bgm/MG_Target.ogg', 30),
    35: ToontownSong(35, TTLocalizer.MusicMgToontag, 'phase_4/audio/bgm/MG_toontag.ogg', 57),
    36: ToontownSong(36, TTLocalizer.MusicMgTravel, 'phase_4/audio/bgm/MG_Travel.ogg', 31),
    37: ToontownSong(37, TTLocalizer.MusicMgTugOWar, 'phase_4/audio/bgm/MG_tug_o_war.ogg', 28),
    38: ToontownSong(38, TTLocalizer.MusicMgTwodgame, 'phase_4/audio/bgm/MG_TwoDGame.ogg', 59),
    39: ToontownSong(39, TTLocalizer.MusicMgVine, 'phase_4/audio/bgm/MG_Vine.ogg', 32),
    40: ToontownSong(40, TTLocalizer.MusicMinigameRace, 'phase_4/audio/bgm/minigame_race.ogg', 77),
    41: ToontownSong(41, TTLocalizer.MusicEstateTheme, 'phase_5/audio/bgm/estate_bgm.ogg', 132),
    42: ToontownSong(42, TTLocalizer.MusicEstateInteriorTheme, 'phase_5/audio/bgm/estate_interior_bgm.ogg', 123),
    43: ToontownSong(43, TTLocalizer.MusicEncntrGeneralBgIndoor, 'phase_7/audio/bgm/encntr_general_bg_indoor.ogg', 31),
    44: ToontownSong(44, TTLocalizer.MusicEncntrGeneralSuitWinningIndoor, 'phase_7/audio/bgm/encntr_suit_winning_indoor.ogg', 36),
    45: ToontownSong(45, TTLocalizer.MusicEncntrToonWinningIndoor, 'phase_7/audio/bgm/encntr_toon_winning_indoor.ogg', 31),
    46: ToontownSong(46, TTLocalizer.MusicTtElevator, 'phase_7/audio/bgm/tt_elevator.ogg', 12),
    47: ToontownSong(47, TTLocalizer.MusicTcEncounter, 'phase_9/audio/bgm/encntr_suit_ttc.ogg', 30),
    48: ToontownSong(48, TTLocalizer.MusicDdEncounter, 'phase_9/audio/bgm/encntr_suit_dd.ogg', 24),
    49: ToontownSong(49, TTLocalizer.MusicDgEncounter, 'phase_9/audio/bgm/encntr_suit_dg.ogg', 29),
    50: ToontownSong(50, TTLocalizer.MusicMmEncounter, 'phase_9/audio/bgm/encntr_suit_mml.ogg', 27),
    51: ToontownSong(51, TTLocalizer.MusicTbEncounter, 'phase_9/audio/bgm/encntr_suit_tb.ogg', 48),
    52: ToontownSong(52, TTLocalizer.MusicDlEncounter, 'phase_9/audio/bgm/encntr_suit_ddl.ogg', 33),
    53: ToontownSong(53, TTLocalizer.MusicEncntrSuitWinning, 'phase_9/audio/bgm/encntr_suit_winning.ogg', 30),
    54: ToontownSong(54, TTLocalizer.MusicEncntrToonWinning, 'phase_9/audio/bgm/encntr_toon_winning.ogg', 29),
    55: ToontownSong(55, TTLocalizer.MusicSbCourtyard, 'phase_9/audio/bgm/encntr_suit_HQ_nbrhood.ogg', 42),
    56: ToontownSong(56, TTLocalizer.MusicChqFactBg, 'phase_9/audio/bgm/CHQ_FACT_bg.ogg', 48),
    57: ToontownSong(57, TTLocalizer.MusicSbBossIntro, 'phase_9/audio/bgm/VP_intro_cutscene.ogg', 46),
    58: ToontownSong(58, TTLocalizer.MusicSbBossBattle1, 'phase_9/audio/bgm/VP_round_1.ogg', 32),
    59: ToontownSong(59, TTLocalizer.MusicSbBossBattle2, 'phase_9/audio/bgm/VP_round_2.ogg', 32),
    60: ToontownSong(60, TTLocalizer.MusicSbBossBattle3, 'phase_9/audio/bgm/encntr_vp_boss.ogg', 36),
    61: ToontownSong(61, TTLocalizer.MusicCbCourtyard, 'phase_9/audio/bgm/CBHQ_nbrhood.ogg', 48),
    62: ToontownSong(62, TTLocalizer.MusicCbMint, 'phase_9/audio/bgm/CBHQ_Mint_bg.ogg', 34),
    63: ToontownSong(63, TTLocalizer.MusicCbSSEncounter, 'phase_9/audio/bgm/CB_courtyard_encntr.ogg', 28),
    64: ToontownSong(64, TTLocalizer.MusicCfoBattle1, 'phase_9/audio/bgm/CFO_round_1.ogg', 34),
    65: ToontownSong(65, TTLocalizer.MusicCfoBattle2, 'phase_9/audio/bgm/CFO_round_2.ogg', 30),
    66: ToontownSong(66, TTLocalizer.MusicCfoBattle3, 'phase_9/audio/bgm/encntr_cfo_boss.ogg', 66),
    67: ToontownSong(67, TTLocalizer.MusicLbCourtyard, 'phase_11/audio/bgm/LB_courtyard.ogg', 32),
    68: ToontownSong(68, TTLocalizer.MusicLbCourtyardEncounter, 'phase_11/audio/bgm/LB_courtyard_encntr.ogg', 54),
    69: ToontownSong(69, TTLocalizer.MusicLbJurybg, 'phase_11/audio/bgm/LB_juryBG.ogg', 54),
    70: ToontownSong(70, TTLocalizer.MusicLbCjFinale, 'phase_11/audio/bgm/encntr_cj_boss.ogg', 35),
    71: ToontownSong(71, TTLocalizer.MusicBossbotEntryV1, 'phase_12/audio/bgm/Bossbot_Entry_v1.ogg', 30),
    72: ToontownSong(72, TTLocalizer.MusicBossbotEntryV2, 'phase_12/audio/bgm/Bossbot_Entry_v2.ogg', 30),
    73: ToontownSong(73, TTLocalizer.MusicBossbotEntryV3, 'phase_12/audio/bgm/Bossbot_Entry_v3.ogg', 29),
    74: ToontownSong(74, TTLocalizer.MusicBossbotFactoryV1, 'phase_12/audio/bgm/Bossbot_Factory_v1.ogg', 30),
    75: ToontownSong(75, TTLocalizer.MusicBossbotFactoryV2, 'phase_12/audio/bgm/Bossbot_Factory_v2.ogg', 30),
    76: ToontownSong(76, TTLocalizer.MusicBossbotFactoryV3, 'phase_12/audio/bgm/Bossbot_Factory_v3.ogg', 30),
    77: ToontownSong(77, TTLocalizer.MusicBossbotCeoV1, 'phase_12/audio/bgm/BossBot_CEO_v1.ogg', 30),
    78: ToontownSong(78, TTLocalizer.MusicBossbotCeoV2, 'phase_12/audio/bgm/BossBot_CEO_v2.ogg', 30),
}

FadeTime = 5
ServerBufferTime = 2


