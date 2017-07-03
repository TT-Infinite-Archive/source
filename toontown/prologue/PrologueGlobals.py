from panda3d.core import Point3


ACTORS = {
    'moochtopher': {
        'npcId': 91921,
        'initial': 'neutral',
        'pos': Point3(85.114, -24.173, 19.785),
        'rotation': Point3(50, 0, 0),
    },
    'gideon': {
        'npcId': 91922,
        'initial': 'neutral',
        'pos': Point3(83.539, -8.610, 4.025),
        'rotation': Point3(199.797, 0, 0),
    },
    'randomNpc1': {
        'npcId': 5124,
        'initial': 'neutral',
        'pos': Point3(79.216, -10.626, 4.025),
        'rotation': Point3(219.058, 0, 0),
    },
    'randomNpc2': {
        'npcId': 2208,
        'initial': 'neutral',
        'pos': Point3(76.664, -14.819, 4.025),
        'rotation': Point3(219.058, 0, 0),
    },
    'flippy': {
        'npcId': 2001,
        'initial': 'neutral',
        'pos': Point3(74.905, 20.077, 5.820),
        'rotation': Point3(91.155, 0, 0),
    },
    'surlee': {
        'npcId': 2019,
        'initial': 'neutral',
        'pos': Point3(74.822, -22.105, 6.051),
        'rotation': Point3(258.403, 0, 0),
    },
    'philip': {
        'npcId': 91924,
        'initial': 'neutral',
        'pos': Point3(97.391, -26.123, 18.840),
        'rotation': Point3(42.999, 0, 0),
    },
    'philipCog': {
        'npcId': 91924,
        'initial': 'neutral',
        'pos': Point3(100.263, -35.361, 24.264),
        'rotation': Point3(49.785, 0, 0),
    }
}

MUSIC = {
    'Ambience': 'phase_4/audio/bgm/storm_ambience.ogg',
    'GovernaughtBrawl': 'phase_4/audio/bgm/encntr_suit_winning_guitar.ogg'
}

SFX = {
    # Philip Neuton Governaught Dial
    'speechExclaim': 'phase_4/audio/dial/av_suit_duck_exclaim.ogg',
    'speechHowl': 'phase_4/audio/dial/av_suit_duck_howl.ogg',
    'speechLong': 'phase_4/audio/dial/av_suit_duck_long.ogg',
    'speechQuestion': 'phase_4/audio/dial/av_suit_duck_question.ogg',
    'speechShort': 'phase_4/audio/dial/av_suit_duck_short.ogg',
    'speechTransition': 'phase_4/audio/dial/av_suit_duck_transition.ogg'
}