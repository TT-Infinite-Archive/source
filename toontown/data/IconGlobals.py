from toontown.data.Icon import Icon

ICON_TEN_DOLLAR = 1
ICON_ONE_DOLLAR = 2
ICON_FIVE_DOLLAR = 3
ICON_ANVIL = 4
ICON_AOOGAH = 5
ICON_BAMBOO_CANE = 6
ICON_BANANA_PEEL = 7
ICON_BIG_MAGNET = 8
ICON_BIKE_HORN = 9
ICON_BUGLE = 10
ICON_CAKE = 11
ICON_CREAM_PIE = 12
ICON_CREAM_PIE_SLICE = 13
ICON_CUPCAKE = 14
ICON_ELEPHANT = 15
ICON_FEATHER = 16
ICON_FIREHOSE = 17
ICON_FLOWER_POT = 18
ICON_FOG_HORN = 19
ICON_FRUIT_PIE = 20
ICON_FRUIT_PIE_SLICE = 21
ICON_GLASS_OF_WATER = 22
ICON_HYPNO_GOGGLES = 23
ICON_JUGGLING_CUBES = 24
ICON_LIPSTICK = 25
ICON_MARBLES = 26
ICON_MEGAPHONE = 27
ICON_PIANO = 28
ICON_PIXIEDUST = 29
ICON_QUICKSAND = 30
ICON_RAKE = 31
ICON_SAFE = 32
ICON_SANDBAG = 33
ICON_SELTZER_BOTTLE = 34
ICON_SMALL_MAGNET = 35
ICON_SQUIRT_FLOWER = 36
ICON_STORM_CLOUD = 37
ICON_TART = 38
ICON_TNT = 39
ICON_TRAP_DOOR = 40
ICON_WATER_GUN = 41
ICON_WHISTLE = 42
ICON_BIG_WEIGHT = 43
ICON_WEDDING_CAKE = 44
ICON_TRAIN_TRACKS = 45
ICON_PRESENTATION = 46
ICON_OPERA_SINGER = 47
ICON_LADDER = 48
ICON_GEYSER = 49
ICON_SHIP = 50
ICON_TROOPER_WHISTLE = 51
ICON_TROOPER_FIST = 52

ICON_CUPCAKE_NEW = 1
ICON_PIESLICE = 2
ICON_GOLD_TART = 3
ICON_PASS = 4
ICON_RED_TART = 5

ICON_REPOSITORY = {
    0: None,
    ICON_CUPCAKE_NEW: Icon('Tart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart'),
    ICON_PIESLICE: Icon('PieSlice', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_fruit_pie_slice'),
    ICON_GOLD_TART: Icon('GoldenTart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.84, 0.0, 1.0)),
    ICON_PASS: Icon('Pass', 'phase_3.5/models/gui/battle_gui', nodePathName='tt_t_gui_bat_pass', scale=0.2),
    ICON_RED_TART: Icon('RedTart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.2, 0.2, 1.0))
}


def getIcon(id):
    return ICON_REPOSITORY[id]

ICON_ID_TO_MODEL = {
    0: None,
    ICON_TEN_DOLLAR: 'phase_3.5/models/gui/inventory_icons',
    ICON_ONE_DOLLAR: 'phase_3.5/models/gui/inventory_icons',
    ICON_FIVE_DOLLAR: 'phase_3.5/models/gui/inventory_icons',
    ICON_ANVIL: 'phase_3.5/models/gui/inventory_icons',
    ICON_AOOGAH: 'phase_3.5/models/gui/inventory_icons',
    ICON_BAMBOO_CANE: 'phase_3.5/models/gui/inventory_icons',
    ICON_BANANA_PEEL: 'phase_3.5/models/gui/inventory_icons',
    ICON_BIG_MAGNET: 'phase_3.5/models/gui/inventory_icons',
    ICON_BIKE_HORN: 'phase_3.5/models/gui/inventory_icons',
    ICON_BUGLE: 'phase_3.5/models/gui/inventory_icons',
    ICON_CAKE: 'phase_3.5/models/gui/inventory_icons',
    ICON_CREAM_PIE: 'phase_3.5/models/gui/inventory_icons',
    ICON_CREAM_PIE_SLICE: 'phase_3.5/models/gui/inventory_icons',
    ICON_CUPCAKE: 'phase_3.5/models/gui/inventory_icons',
    ICON_ELEPHANT: 'phase_3.5/models/gui/inventory_icons',
    ICON_FEATHER: 'phase_3.5/models/gui/inventory_icons',
    ICON_FIREHOSE: 'phase_3.5/models/gui/inventory_icons',
    ICON_FLOWER_POT: 'phase_3.5/models/gui/inventory_icons',
    ICON_FOG_HORN: 'phase_3.5/models/gui/inventory_icons',
    ICON_FRUIT_PIE: 'phase_3.5/models/gui/inventory_icons',
    ICON_FRUIT_PIE_SLICE: 'phase_3.5/models/gui/inventory_icons',
    ICON_GLASS_OF_WATER: 'phase_3.5/models/gui/inventory_icons',
    ICON_HYPNO_GOGGLES: 'phase_3.5/models/gui/inventory_icons',
    ICON_JUGGLING_CUBES: 'phase_3.5/models/gui/inventory_icons',
    ICON_LIPSTICK: 'phase_3.5/models/gui/inventory_icons',
    ICON_MARBLES: 'phase_3.5/models/gui/inventory_icons',
    ICON_MEGAPHONE: 'phase_3.5/models/gui/inventory_icons',
    ICON_PIANO: 'phase_3.5/models/gui/inventory_icons',
    ICON_PIXIEDUST: 'phase_3.5/models/gui/inventory_icons',
    ICON_QUICKSAND: 'phase_3.5/models/gui/inventory_icons',
    ICON_RAKE: 'phase_3.5/models/gui/inventory_icons',
    ICON_SAFE: 'phase_3.5/models/gui/inventory_icons',
    ICON_SANDBAG: 'phase_3.5/models/gui/inventory_icons',
    ICON_SELTZER_BOTTLE: 'phase_3.5/models/gui/inventory_icons',
    ICON_SMALL_MAGNET: 'phase_3.5/models/gui/inventory_icons',
    ICON_SQUIRT_FLOWER: 'phase_3.5/models/gui/inventory_icons',
    ICON_STORM_CLOUD: 'phase_3.5/models/gui/inventory_icons',
    ICON_TART: 'phase_3.5/models/gui/inventory_icons',
    ICON_TNT: 'phase_3.5/models/gui/inventory_icons',
    ICON_TRAP_DOOR: 'phase_3.5/models/gui/inventory_icons',
    ICON_WATER_GUN: 'phase_3.5/models/gui/inventory_icons',
    ICON_BIG_WEIGHT: 'phase_3.5/models/gui/inventory_icons',
    ICON_WHISTLE: 'phase_3.5/models/gui/inventory_icons',
    ICON_WEDDING_CAKE: 'phase_3.5/models/gui/inventory_icons',
    ICON_TRAIN_TRACKS: 'phase_3.5/models/gui/inventory_icons',
    ICON_PRESENTATION: 'phase_3.5/models/gui/inventory_icons',
    ICON_OPERA_SINGER: 'phase_3.5/models/gui/inventory_icons',
    ICON_LADDER: 'phase_3.5/models/gui/inventory_icons',
    ICON_GEYSER: 'phase_3.5/models/gui/inventory_icons',
    ICON_SHIP: 'phase_3.5/models/gui/inventory_icons',
    ICON_TROOPER_WHISTLE: 'phase_3.5/models/gui/tt_m_gui_gm_toontroop_getConnected',
    ICON_TROOPER_FIST: 'phase_3.5/models/gui/tt_m_gui_gm_toonResistance_fist',
}

ICON_ID_TO_NODE = {
    0: None,
    ICON_TEN_DOLLAR: '**/inventory_10dollarbill',
    ICON_ONE_DOLLAR: '**/inventory_1dollarbill',
    ICON_FIVE_DOLLAR: '**/inventory_5dollarbill',
    ICON_ANVIL: '**/inventory_anvil',
    ICON_AOOGAH: '**/inventory_aoogah',
    ICON_BAMBOO_CANE: '**/inventory_bamboo_cane',
    ICON_BANANA_PEEL: '**/inventory_bannana_peel',
    ICON_BIG_MAGNET: '**/inventory_big_magnet',
    ICON_BIKE_HORN: '**/inventory_bikehorn',
    ICON_BUGLE: '**/inventory_bugle',
    ICON_CAKE: '**/inventory_cake',
    ICON_CREAM_PIE: '**/inventory_creampie',
    ICON_CREAM_PIE_SLICE: '**/inventory_cream_pie_slice',
    ICON_CUPCAKE: '**/inventory_cup_cake',
    ICON_ELEPHANT: '**/inventory_elephant',
    ICON_FEATHER: '**/inventory_feather',
    ICON_FIREHOSE: '**/inventory_firehose',
    ICON_FLOWER_POT: '**/inventory_flower_pot',
    ICON_FOG_HORN: '**/inventory_fog_horn',
    ICON_FRUIT_PIE: '**/inventory_fruitpie',
    ICON_FRUIT_PIE_SLICE: '**/inventory_fruit_pie_slice',
    ICON_GLASS_OF_WATER: '**/inventory_glass_of_water',
    ICON_HYPNO_GOGGLES: '**/inventory_hypno_goggles',
    ICON_JUGGLING_CUBES: '**/inventory_juggling_cubes',
    ICON_LIPSTICK: '**/inventory_lipstick',
    ICON_MARBLES: '**/inventory_marbles',
    ICON_MEGAPHONE: '**/inventory_megaphone',
    ICON_PIANO: '**/inventory_piano',
    ICON_PIXIEDUST: '**/inventory_pixiedust',
    ICON_QUICKSAND: '**/inventory_quicksand_icon',
    ICON_RAKE: '**/inventory_rake',
    ICON_SAFE: '**/inventory_safe_box',
    ICON_SANDBAG: '**/inventory_sandbag',
    ICON_SELTZER_BOTTLE: '**/inventory_seltzer_bottle',
    ICON_SMALL_MAGNET: '**/inventory_small_magnet',
    ICON_SQUIRT_FLOWER: '**/inventory_squirt_flower',
    ICON_STORM_CLOUD: '**/inventory_storm_cloud',
    ICON_TART: '**/inventory_tart',
    ICON_TNT: '**/inventory_tnt',
    ICON_TRAP_DOOR: '**/inventory_trapdoor',
    ICON_WATER_GUN: '**/inventory_water_gun',
    ICON_BIG_WEIGHT: '**/inventory_weight',
    ICON_WHISTLE: '**/inventory_whistle',
    ICON_WEDDING_CAKE: '**/inventory_wedding',
    ICON_TRAIN_TRACKS: '**/inventory_traintracks',
    ICON_PRESENTATION: '**/inventory_screen',
    ICON_OPERA_SINGER: '**/inventory_opera_singer',
    ICON_LADDER: '**/inventory_ladder',
    ICON_GEYSER: '**/inventory_geyser',
    ICON_SHIP: '**/inventory_ship',
    ICON_TROOPER_WHISTLE: '**/whistleIcon',
    ICON_TROOPER_FIST: '**/*fistIcon',
}

ICON_ID_TO_UNIFORM_SCALE = {
    0: None,
    ICON_TROOPER_WHISTLE: (0.3, 0.3, 0.3),
    ICON_TROOPER_FIST: (0.3, 0.3, 0.3),
}

ICON_ID_TO_UNIFORM_POS = {
    0: None,
    ICON_TROOPER_WHISTLE: (0.0, 0.0, -0.35),
    ICON_TROOPER_FIST: (0.0, 0.0, -0.35),
}