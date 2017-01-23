from toontown.data.Icon import Icon, ImageIcon

ICON_CUPCAKE_NEW = 1
ICON_PIESLICE = 2
ICON_GOLD_TART = 3
ICON_PASS = 4
ICON_RED_TART = 5
ICON_GLOW = 6
ICON_CREAM_PIE_SLICE = 7
ICON_CREAM_PIE = 8
ICON_FRUIT_PIE = 9
ICON_BIRTHDAY_CAKE = 10
ICON_CANNON = 11

ICON_REPOSITORY = {
    0: None,
    ICON_CUPCAKE_NEW: Icon('Tart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart'),
    ICON_PIESLICE: Icon('Pie Slice', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_fruit_pie_slice'),
    ICON_GOLD_TART: Icon('Golden Tart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.84, 0.0, 1.0)),
    ICON_PASS: Icon('Pass', 'phase_3.5/models/gui/battle_gui', nodePathName='tt_t_gui_bat_pass', scale=0.2),
    ICON_RED_TART: Icon('Red Tart', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_tart', color=(1, 0.2, 0.2, 1.0)),
    ICON_GLOW: ImageIcon('Glow', 'phase_3.5/maps/glow.png', scale=(0.003, 0.003, 0.003)),
    ICON_CREAM_PIE_SLICE: Icon('Cream Pie Slice', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_cream_pie_slice'),
    ICON_CREAM_PIE: Icon('Cream Pie', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_creampie'),
    ICON_FRUIT_PIE: Icon('Fruit Pie', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_fruitpie'),
    ICON_BIRTHDAY_CAKE: Icon('Birthday Cake', 'phase_3.5/models/gui/inventory_icons', nodePathName='inventory_cake'),
    ICON_CANNON: ImageIcon('Cannon', 'phase_3.5/maps/toon_cannon.png', scale=0.00025),
}


def getIcon(id):
    return ICON_REPOSITORY[id]
