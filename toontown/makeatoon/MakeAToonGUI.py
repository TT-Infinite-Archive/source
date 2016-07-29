from pandac.PandaModules import WindowProperties
from panda3d.core import *
from direct.gui.DirectGui import *
from toontown.toonbase.TTLocalizer import SBshuffleBtn
from toontown.toon.ColorDNA import convertToRgb, convertToHsv
from MakeAToonGlobals import *
import math


preloaded = {}


def loadModels():
    global preloaded
    if not preloaded:
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        preloaded['guiRArrowUp'] = gui.find('**/tt_t_gui_mat_arrowUp')
        preloaded['guiRArrowRollover'] = gui.find('**/tt_t_gui_mat_arrowUp')
        preloaded['guiRArrowDown'] = gui.find('**/tt_t_gui_mat_arrowDown')
        preloaded['guiRArrowDisabled'] = gui.find('**/tt_t_gui_mat_arrowDisabled')
        preloaded['shuffleFrame'] = gui.find('**/tt_t_gui_mat_shuffleFrame')
        preloaded['shuffleUp'] = gui.find('**/tt_t_gui_mat_shuffleUp')
        preloaded['shuffleDown'] = gui.find('**/tt_t_gui_mat_shuffleDown')
        preloaded['shuffleArrowUp'] = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        preloaded['shuffleArrowDown'] = gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        preloaded['shuffleArrowRollover'] = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        preloaded['shuffleArrowDisabled'] = gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        gui.removeNode()
        del gui


class MATFrame(DirectFrame):
    def __init__(self, parent=None, arrowcommand=None, wantArrows=True, text_scale=(-0.001, -0.015), **kw):
        loadModels()

        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('image', preloaded['shuffleFrame'], None),
            ('relief', None, None),
            ('frameColor', (1, 1, 1, 1), None),
            ('image_scale', halfButtonInvertScale, None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_scale', text_scale, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(MATFrame)

        if not wantArrows:
            self.leftArrow = None
            self.rightArrow = None
            return

        self.leftArrow = MATArrow(parent=self, command=arrowcommand)
        self.rightArrow = MATArrow(parent=self, inverted=True, command=arrowcommand)

    def destroy(self):
        if self.leftArrow:
            self.leftArrow.destroy()
        if self.rightArrow:
            self.rightArrow.destroy()

        DirectFrame.destroy(self)


class MATArrow(DirectButton):
    def __init__(self, parent=None, inverted=False, **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        if not inverted:
            scales = (halfButtonScale, halfButtonHoverScale)
            extraArgs = [-1]
            pos = (-0.2, 0, 0)
        else:
            scales = (halfButtonInvertScale, halfButtonInvertHoverScale)
            extraArgs = [1]
            pos = (0.2, 0, 0)

        optiondefs = (
            ('relief', None, None),
            ('image', (
                preloaded['shuffleArrowUp'],
                preloaded['shuffleArrowDown'],
                preloaded['shuffleArrowRollover'],
                preloaded['shuffleArrowDisabled']
            ), None),
            ('image_scale', scales[0], None),
            ('image1_scale', scales[1], None),
            ('image2_scale', scales[1], None),
            ('extraArgs', extraArgs, None),
            ('pos', pos, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MATArrow)


class MATSlider(DirectSlider):
    def __init__(self, parent=None, labelText='', **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('thumb_image', (
                preloaded['shuffleUp'],
                preloaded['shuffleDown'],
                preloaded['shuffleUp']
            ), None),
            ('thumb_relief', None, None),
            ('pageSize', 0.5, None),
            ('scale', 0.32, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectSlider.__init__(self, parent)
        self.initialiseoptions(MATSlider)

        self.label = None

        if labelText:
            self.label = DirectLabel(parent=self, pos=(0, 0, 0.1), text_bg=(0, 0, 0, 0), text_shadow=(0, 0, 0, 1),
                                     text_scale=0.3, text_fg=VBase4(1.0, 1.0, 1.0, 1.0), text=labelText, relief=None)

    def getColor(self):
        return self['value'] / 100.0

    def destroy(self):
        if self.label:
            self.label.destroy()

        DirectSlider.destroy(self)


class MATShuffleButton(DirectButton):
    def __init__(self, wantArrows=True, parent=None, arrowcommand=None, **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('relief', None, None),
            ('image', (
                preloaded['shuffleUp'],
                preloaded['shuffleDown'],
                preloaded['shuffleUp']
            ), None),
            ('image_scale', halfButtonInvertScale if not kw.get('image_scale') else kw['image_scale'], None),
            ('image1_scale', (-0.63, 0.6, 0.6) if not kw.get('image1_scale') else kw['image1_scale'], None),
            ('image2_scale', (-0.63, 0.6, 0.6) if not kw.get('image2_scale') else kw['image2_scale'], None),
            ('text_pos', (0, -0.02) if not kw.get('text_pos') else kw['text_pos'], None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_shadow', (0, 0, 0, 1), None),
            ('text_scale', SBshuffleBtn if not kw.get('text_scale') else kw['text_scale'], None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MATShuffleButton)

        if not wantArrows:
            self.leftArrow = None
            self.rightArrow = None
            self.frame = None
            return

        self.leftArrow = MATArrow(parent=self, command=arrowcommand)
        self.rightArrow = MATArrow(parent=self, command=arrowcommand, inverted=True)

        self.frame = MATFrame(parent=parent, wantArrows=False)

    def destroy(self):
        if self.leftArrow:
            self.leftArrow.destroy()
        if self.rightArrow:
            self.rightArrow.destroy()
        if self.frame:
            self.frame.destroy()
        DirectButton.destroy(self)

    def showArrows(self):
        self.leftArrow.show()
        self.rightArrow.show()

    def hideArrows(self):
        self.leftArrow.hide()
        self.rightArrow.hide()

class MATAdvancedColorPicker(DirectFrame):
    def load(self):
        # Our color data
        self.raw_hsv = [0, 0, 0]
        self.hsv = [0, 0, 0]
        self.rgb = (0, 0, 0)
        
        self.buttonDown = False
        self.announceEvent = None

        # Frame size
        self.setScale(0.25)
        
        # Color Wheel
        self.wheel = DirectFrame(
            parent=self,
            image='phase_3/maps/wheel.png',
            relief=None,
            state=DGG.NORMAL
        )
        self.wheel.setTransparency(TransparencyAttrib.MAlpha)

        self.wheel.bind(DGG.ENTER, self.__enterWheel)
        self.wheel.bind(DGG.EXIT, self.__exitWheel)
        self.wheel.bind(DGG.B1PRESS, self.__startPlacing)
        self.wheel.bind(DGG.B1RELEASE, self.__stopPlacing)
    
        # The Overlay
        self.overlay = OnscreenImage(
            parent=self,
            image='phase_3/maps/overlay.png'
        )
        self.overlay.setTransparency(TransparencyAttrib.MAlpha)
        
        # The Pointer
        self.pointer = OnscreenImage(
            parent=aspect2d,
            image='phase_3/maps/pointer.png'
        )
        self.pointer.setTransparency(TransparencyAttrib.MAlpha)
        self.pointer.setScale(0.055)
        
        # The Value Bar
        self.valueBar = DirectSlider(
            parent=self,
            relief=None,
            orientation='vertical',
            image='phase_3/maps/value_bar.png',
            thumb_image='phase_3/maps/value_pointer.png',
            thumb_relief=None,
            thumb_image_scale=(1.6, 1, 0.3),
            command=self.__setValue,
            value = 90,
            range=(55, 90)
        )
        self.valueBar.setTransparency(TransparencyAttrib.MAlpha)
        self.valueBar.setPos(1.5, 0, 0)
        self.valueBar.setScale(0.25, 1, 1)
        
        # The Input Box
        self.inputBox = DirectEntry(
            parent=self,
            command=self.__setFromText,
            relief=None,
            image='phase_3/maps/input_box.png',
            image_pos=(4.5, 1, 0.2),
            image_scale=(5, 0, 0.75)
        )
        self.inputBox.bind(DGG.TYPE, self.__setFromText)
        self.inputBox.setTransparency(TransparencyAttrib.MAlpha)
        self.inputBox.setPos(-0.95, 0, -1.6)
        self.inputBox.setScale(0.3, 0.4, 0.4)
        
    def destroy(self):
        self.__exitWheel(0)
        
        if self.wheel:
            self.wheel.destroy()
            self.wheel = None
        
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            
        if self.pointer:
            self.pointer.destroy()
            self.pointer = None
            
        if self.valueBar:
            self.valueBar.destroy()
            self.valueBar = None
        
        if self.inputBox:
            self.inputBox.destroy()
            self.inputBox = None
        
        DirectFrame.destroy(self)
        
    def __wheelTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            x=base.mouseWatcherNode.getMouseX()
            y=base.mouseWatcherNode.getMouseY()
        else:
            return task.done

        # Centre of the wheel
        center_x = self.wheel.getX(render2d)
        center_y = self.wheel.getZ(render2d)

        # Window properties
        props = WindowProperties()
        
        # Are we inside the wheel?
        dist = math.sqrt(((center_x - x) ** 2) + ((center_y - y) ** 2))
        radius = render2d.getRelativePoint(self.wheel, (
                self.wheel.getX() + (self.wheel.getWidth() / 2.0),
                0,
                self.wheel.getZ() + (self.wheel.getHeight() / 2.0)
            )
        )

        if dist < radius[2]:
            if self.buttonDown:
                props.setCursorHidden(True)

                # Get the hue, saturation and value.
                hue = math.degrees(math.atan2(center_x - x, center_y - y))
                sat = (dist / 0.23) * 100

                # We want hue as a direction 0-360
                if hue < 0:
                    hue += 360

                # Set our properties
                self.setHsv(hue, sat, self.raw_hsv[2])
            else:
                props.setCursorHidden(False)
                
        # Continue the task!
        base.win.requestProperties(props)
        return task.cont
        
    def __enterWheel(self, event):
        # Start tracking our mouse pointer
        taskMgr.add(self.__wheelTask, 'MATColorWheel-mouse')
        
    def __exitWheel(self, event):
        # Window properties
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)
        
        # Stop tracking our mouse pointer
        taskMgr.remove('MATColorWheel-mouse')
        
    def __startPlacing(self, event):
        self.buttonDown = True
    
    def __stopPlacing(self, event):
        self.buttonDown = False
        
    def __calculateValues(self):
        self.hsv = [
            self.raw_hsv[0] / 360.0,
            self.raw_hsv[1] / 100.0,
            self.raw_hsv[2] / 100.0
        ]
        self.rgb = convertToRgb(*self.hsv)
        
        rgb = (
            int(self.rgb[0] * 255),
            int(self.rgb[1] * 255),
            int(self.rgb[2] * 255),
        )
        
        self.inputBox.set('#%02x%02x%02x' % rgb)
        if self.announceEvent is not None:
            messenger.send(self.announceEvent)
        
    def __setValue(self):
        self.raw_hsv[2] = self.valueBar['value']
        self.setHsv(*self.raw_hsv)
        
    def __setFromText(self, text=None):
        if text is None:
            text = self.inputBox.get()

        if type(text) != str:
            text = self.inputBox.get()

        if len(text) < 7:
            return

        red = "0x" + text[1:3]
        green = "0x" + text[3:5]
        blue = "0x" + text[5:7]

        print (red, green, blue)
        
        try:
            self.setRgb(
                int(red, 0) / 255.0,
                int(green, 0) / 255.0,
                int(blue, 0) / 255.0
            )
        except:
            pass
        
    def setHsv(self, hue, saturation, value):    
        # Color legitimacy checks
        hue = min(hue, 360)
        
        # Add limits
        saturation = min(max(saturation, 20), 88)
        value = min(max(value, 55), 90)
        
        # Strong colors need to be changed a little
        # TODO
        
        self.raw_hsv = [hue, saturation, value]
        if self.valueBar['value'] != value:
            self.valueBar['value'] = value
        
        value /= 100.0
        self.wheel.setColor(value, value, value)
        self.__calculateValues()
        
        saturation /= 100.0
        saturation *= 0.23
        
        x = self.wheel.getX(render2d) + (-saturation * math.sin(math.radians(hue)))
        y = self.wheel.getZ(render2d) + (-saturation * math.cos(math.radians(hue)))
        self.pointer.setPos(render2d, x + 0.022, 0.0, y + 0.022)
        
    def setRgb(self, red, green, blue, alpha=1.0):
        red = min(red, 255)
        if red > 1:
            red /= 255.0
        
        green = min(green, 255)
        if green > 1:
            green /= 255.0
            
        blue = min(blue, 255)
        if blue > 1:
            blue /= 255.0
        
        hsv = convertToHsv(red, green, blue)
        self.setHsv(hsv[0] * 360, hsv[1] * 100, hsv[2] * 100)
        
    def getHsv(self):
        return tuple(self.hsv)
        
    def getRgb(self):
        return self.rgb

    def setAnnounceEvent(self, event):
        self.announceEvent = event

    def hide(self):
        DirectFrame.hide(self)
        self.pointer.hide()

    def show(self):
        DirectFrame.show(self)
        self.pointer.show()