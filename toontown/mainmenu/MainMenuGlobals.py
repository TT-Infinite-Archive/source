from panda3d.core import TextNode
from direct.gui.DirectGui import DGG
from toontown.toonbase import TTLocalizer, ToontownGlobals, ColorGlobals
from toontown.toontowngui.TTLabel import TTLabel
from pandac.PandaModules import Vec4


LABEL_PROPERTIES = {
    'text_fg': ColorGlobals.CDefault,
    'text_font': ToontownGlobals.getToonFont(),
    'text_size': TTLabel.GiantSize,
    'text_wordwrap': 25
}
ENTRY_PROPERTIES = {
    'relief': DGG.GROOVE,
    'scale': 0.1,
    'borderWidth': (0.05, 0.05),
    'frameColor': (
        (1, 1, 1, 1),
        (1, 1, 1, 1,),
        (0.5, 0.5, 0.5, 0.5)),
    'state': DGG.NORMAL,
    'text_align': TextNode.ACenter,
    'text_scale': TTLocalizer.OPCodesInputTextScale,
    'numLines': 1,
    'focus': 1,
    'backgroundFocus': 0,
    'cursorKeys': 1,
    'text_fg': ColorGlobals.CBlack,
    'suppressMouse': 1,
    'autoCapitalize': 0
}

buttonScale = (-1.1, 1.1, 1.1),
buttonScale_clickhover = (-1.2, 1.2, 1.2)

BUTTON_PROPERTIES = {
    'wantArrows': False,
    'image_scale': buttonScale,
    'image2_scale': buttonScale_clickhover,
    'image1_scale': buttonScale_clickhover,
    'text_scale': 0.09,
    'text2_scale': 0.095,
    'text1_scale': 0.095
}
BUTTON_PROPERTIES_2 = {
    'wantArrows': False,
    'image_scale': buttonScale,
    'image2_scale': buttonScale_clickhover,
    'image1_scale': buttonScale_clickhover,
    'text_scale': 0.10,
    'text2_scale': 0.105,
    'text1_scale': 0.105
}
BUTTON_PROPERTIES_3 = {
    'wantArrows': False,
    'image_scale': buttonScale,
    'image2_scale': buttonScale_clickhover,
    'image1_scale': buttonScale_clickhover,
    'text_scale': 0.08,
    'text2_scale': 0.085,
    'text1_scale': 0.085
}

gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')

guiAcceptUp = gui.find('**/tt_t_gui_mat_okUp')
guiAcceptUp.flattenStrong()
guiAcceptDown = gui.find('**/tt_t_gui_mat_okDown')
guiAcceptDown.flattenStrong()
guiNextUp = gui.find('**/tt_t_gui_mat_nextUp')
guiNextUp.flattenStrong()
guiNextDown = gui.find('**/tt_t_gui_mat_nextDown')
guiNextDown.flattenStrong()

halfButtonScale = (0.6, 0.6, 0.6)
halfButtonHoverScale = (0.7, 0.7, 0.7)

START_BUTTON = {
    'relief': None,
    'image': (guiAcceptUp, guiAcceptDown, guiAcceptUp, guiAcceptDown),
    'image_scale': halfButtonScale,
    'image1_scale': halfButtonHoverScale,
    'image2_scale': halfButtonHoverScale,
    'text_fg': (1, 1, 1, 1),
    'text_shadow': (0, 0, 0, 1),
    'text_font': ToontownGlobals.getInterfaceFont(),
    'text_scale': 0.08,
    'text_pos': (0.075, 0.13)

}
MINIATURE_BACK_BUTTON = {
    'relief': None,
    'image': (guiNextUp, guiNextDown, guiNextUp, guiNextDown),
    'image3_color': Vec4(0.5, 0.5, 0.5, 0.75),
    'image_scale': (-0.3, 0.3, 0.3),
    'image1_scale': (-0.35, 0.35, 0.35),
    'image2_scale': (-0.35, 0.35, 0.35),
    'text': ('', TTLocalizer.MakeAToonLast, TTLocalizer.MakeAToonLast, ''),
    'text_font': ToontownGlobals.getInterfaceFont(),
    'text_scale': 0.08,
    'text_pos': (0, 0.115),
    'text_fg': (1, 1, 1, 1),
    'text_shadow': (0, 0, 0, 1)

}
