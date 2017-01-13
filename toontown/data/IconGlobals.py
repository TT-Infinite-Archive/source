from toontown.data.Icon import Icon, ImageIcon

ICON_CUPCAKE_NEW = 1
ICON_PIESLICE = 2
ICON_GOLD_TART = 3
ICON_PASS = 4
ICON_RED_TART = 5
ICON_GLOW = 6
ICON_CREAM_PIESLICE = 7
ICON_CREAM_PIE = 8


ICON_REPOSITORY = {
    0: None,
    ICON_CUPCAKE_NEW: Icon('Tart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart'),
    ICON_PIESLICE: Icon('PieSlice', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_fruit_pie_slice'),
    ICON_GOLD_TART: Icon('GoldenTart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.84, 0.0, 1.0)),
    ICON_PASS: Icon('Pass', 'phase_3.5/models/gui/battle_gui', nodePathName='tt_t_gui_bat_pass', scale=0.2),
    ICON_RED_TART: Icon('RedTart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.2, 0.2, 1.0)),
    ICON_GLOW: ImageIcon('Glow', 'phase_3.5/maps/glow.png', scale=(0.003, 0.003, 0.003))
}


def getIcon(id):
    return ICON_REPOSITORY[id]
