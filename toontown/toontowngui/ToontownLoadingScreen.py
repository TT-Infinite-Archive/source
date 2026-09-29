from panda3d.core import TextNode, Texture, TransparencyAttrib
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownClientGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood import ZoneUtil
import math
import random


LOADING_SCREEN_SORT_INDEX = 4000


class ToontownLoadingScreen:

    FillRate = 6.0
    defaultBarColor = (1.0, 0.75, 0.1, 1)
    cogHQBarColor = (0.4, 0.43, 0.48, 1)
    hood2barColor = {
        ToontownGlobals.DonaldsDock : (0.25, 0.6, 1.0, 1),
        ToontownGlobals.TheBrrrgh : (0.55, 0.85, 1.0, 1),
        ToontownGlobals.MinniesMelodyland : (0.85, 0.4, 0.9, 1),
        ToontownGlobals.DaisyGardens : (0.4, 0.8, 0.25, 1),
        ToontownGlobals.OutdoorZone : (0.85, 0.55, 0.2, 1),
        ToontownGlobals.GoofySpeedway : (1.0, 0.35, 0.2, 1),
        ToontownGlobals.DonaldsDreamland : (0.45, 0.4, 0.85, 1),
        ToontownGlobals.GolfZone : (0.45, 0.75, 0.3, 1)
    }
    defaultTex = 'phase_3.5/maps/loading/default.jpg'
    zone2picture = {
        ToontownGlobals.GoofySpeedway : 'phase_3.5/maps/loading/gs.jpg',
        ToontownGlobals.ToontownCentral : 'phase_3.5/maps/loading/ttc.jpg',
        ToontownGlobals.SillyStreet : 'phase_3.5/maps/loading/ttc_ss.jpg',
        ToontownGlobals.LoopyLane : 'phase_3.5/maps/loading/ttc_ll.jpg',
        ToontownGlobals.PunchlinePlace : 'phase_3.5/maps/loading/ttc_pp.jpg',
        ToontownGlobals.DonaldsDock : 'phase_3.5/maps/loading/dd.jpg',
        ToontownGlobals.BarnacleBoulevard : 'phase_3.5/maps/loading/dd_bb.jpg',
        ToontownGlobals.SeaweedStreet : 'phase_3.5/maps/loading/dd_ss.jpg',
        ToontownGlobals.LighthouseLane : 'phase_3.5/maps/loading/dd_ll.jpg',
        ToontownGlobals.DaisyGardens : 'phase_3.5/maps/loading/dg.jpg',
        ToontownGlobals.ElmStreet : 'phase_3.5/maps/loading/dg_es.jpg',
        ToontownGlobals.MapleStreet : 'phase_3.5/maps/loading/dg_ms.jpg',
        ToontownGlobals.OakStreet : 'phase_3.5/maps/loading/dg_os.jpg',
        ToontownGlobals.MinniesMelodyland : 'phase_3.5/maps/loading/mml.jpg',
        ToontownGlobals.AltoAvenue : 'phase_3.5/maps/loading/mml_aa.jpg',
        ToontownGlobals.BaritoneBoulevard : 'phase_3.5/maps/loading/mml_bb.jpg',
        ToontownGlobals.TenorTerrace : 'phase_3.5/maps/loading/mml_tt.jpg',
        ToontownGlobals.TheBrrrgh : 'phase_3.5/maps/loading/tb.jpg',
        ToontownGlobals.WalrusWay : 'phase_3.5/maps/loading/tb_ww.jpg',
        ToontownGlobals.SleetStreet : 'phase_3.5/maps/loading/tb_ss.jpg',
        ToontownGlobals.PolarPlace : 'phase_3.5/maps/loading/tb_pp.jpg',
        ToontownGlobals.DonaldsDreamland : 'phase_3.5/maps/loading/ddl.jpg',
        ToontownGlobals.LullabyLane : 'phase_3.5/maps/loading/ddl_ll.jpg',
        ToontownGlobals.PajamaPlace : 'phase_3.5/maps/loading/ddl_pp.jpg',
        ToontownGlobals.OutdoorZone : 'phase_3.5/maps/loading/oz.jpg',
        ToontownGlobals.GolfZone : 'phase_3.5/maps/loading/gz.jpg',
        ToontownGlobals.SellbotHQ : 'phase_3.5/maps/loading/sbhq.jpg',
        ToontownGlobals.CashbotHQ : 'phase_3.5/maps/loading/cbhq.jpg',
        ToontownGlobals.LawbotHQ : 'phase_3.5/maps/loading/lbhq.jpg',
        ToontownGlobals.BossbotHQ : 'phase_3.5/maps/loading/bbhq.jpg'
    }

    def __init__(self):
        self.__expectedCount = 0
        self.__count = 0
        self.__showingGui = False
        self.__active = False
        self.gui = loader.loadModel('phase_3/models/gui/progress-background.bam')
        self.title = DirectLabel(guiId='ToontownLoadingScreenTitle', parent=self.gui, relief=None, pos=(0, 0, 0.24), text='', textMayChange=1, text_scale=0.1, text_fg=(1, 1, 2, 0.85), text_align=TextNode.ACenter, text_font=ToontownGlobals.getSignFont())
        barRight = base.a2dRight - max(base.a2dRight / 4.95, 0.36)
        self.waitBar = DirectWaitBar(guiId='ToontownLoadingScreenWaitBar', parent=self.gui, frameSize=(-barRight, barRight, -0.05, 0.05), pos=(0, 0, 0.15), text='',
                                     relief=DGG.TEXTUREBORDER, frameTexture='phase_3/maps/value_bar.png', frameColor=(1, 1, 1, 1), borderWidth=(0.018, 0.018), borderUvWidth=(0.2, 0.06),
                                     barRelief=DGG.TEXTUREBORDER, barTexture='phase_3/maps/curved-gui-square.png', barColor=self.defaultBarColor, barBorderWidth=(0.015, 0.015))
        self.waitBar.barStyle.setUvWidth(0.02, 0.02)
        self.waitBar.updateBarStyle()
        self.waitBar.setTransparency(TransparencyAttrib.MAlpha)
        self.toon = None
        self.toonDNA = None
        base.finalExitCallbacks.append(self.__removeToon)
        logoScale = 0.5625  # Scale for our locked aspect ratio (2:1).
        offset = -0.04
        self.logo = OnscreenImage(
            image='phase_3/maps/toontown_infinite_logo.png',
            scale=(0.9, 0.35, 0.45))
        self.logo.reparentTo(hidden)
        self.logo.setTransparency(TransparencyAttrib.MAlpha)
        scale = self.logo.getScale()
        # self.logo.setPos(scale[0], 0, -scale[2])
        self.logo.setPos(offset, 0, -0.45)

    def destroy(self):
        self.__removeToon()
        self.waitBar.destroy()
        self.title.destroy()
        self.gui.removeNode()
        self.logo.removeNode()

    def __removeToon(self):
        if self.toon:
            self.toon.delete()
            self.toon = None
            self.toonDNA = None

    def __updateToon(self):
        dna = base.localAvatarStyle
        if dna is None:
            self.__removeToon()
            return
        netString = dna.makeNetString()
        if netString == self.toonDNA:
            return
        from toontown.toon import Toon, ToonDNA
        self.__removeToon()
        style = ToonDNA.ToonDNA()
        style.makeFromNetString(netString)
        self.toon = Toon.Toon()
        self.toon.setDNA(style)
        self.toon.cleanupNametag()
        self.toon.deleteDropShadow()
        self.toon.useLOD(1000)
        self.toon.getGeomNode().setDepthTest(1)
        self.toon.getGeomNode().setDepthWrite(1)
        self.toon.setH(-110)
        self.toon.setScale(0.085)
        self.toon.setPos(self.waitBar['frameSize'][0] - 0.13, 0, -0.08)
        self.toon.reparentTo(self.waitBar)
        self.toon.loop('run')
        self.toonDNA = netString

    def getTip(self, tipCategory):
        return TTLocalizer.TipTitle + '\n' + random.choice(TTLocalizer.TipDict.get(tipCategory))

    def begin(self, range, label, gui, tipCategory, zoneId):
        self.waitBar['range'] = range
        self.__count = 0
        self.__expectedCount = range
        self.__lastFrameT = globalClock.getRealTime()
        self.__updateToon()
        self.__showingGui = gui
        self.__active = True
        self.__setDestination(label, zoneId)
        self.waitBar.update(self.__count)

    def extend(self, range, label, zoneId):
        self.__expectedCount = max(self.__expectedCount, self.__count + range)
        self.waitBar['range'] = self.__expectedCount
        self.__setDestination(label, zoneId)

    def __setDestination(self, label, zoneId):
        self.title['text'] = label
        if ToontownGlobals.BossbotHQ <= zoneId <= ToontownGlobals.LawbotHQ:
            self.title['text_font'] = ToontownClientGlobals.getSuitFont()
            self.waitBar['barColor'] = self.cogHQBarColor
        else:
            self.title['text_font'] = ToontownGlobals.getSignFont()
            self.waitBar['barColor'] = self.hood2barColor.get(ZoneUtil.getHoodId(zoneId), self.defaultBarColor)
        self.backgroundPath = self.zone2picture.get(ZoneUtil.getBranchZone(zoneId), self.defaultTex)
        self.__updateVisibility()

    def __updateVisibility(self):
        self.waitBar.reparentTo(self.gui)
        self.title.reparentTo(self.gui)
        self.gui.reparentTo(hidden)
        self.logo.reparentTo(hidden)
        if not self.__active:
            return
        if self.__showingGui:
            self.title.setPos(0, 0, 0.26)
            self.gui.setPos(0, -0.1, 0)
            self.gui.reparentTo(aspect2d, LOADING_SCREEN_SORT_INDEX)
            self.background = loader.loadTexture(self.backgroundPath)
            self.gui.setTexture(self.background, 1)
            if self.backgroundPath == self.defaultTex:
                self.logo.reparentTo(base.a2dpTopCenter, LOADING_SCREEN_SORT_INDEX)
        self.title.reparentTo(base.a2dpBottomCenter, LOADING_SCREEN_SORT_INDEX)
        self.waitBar.reparentTo(base.a2dpBottomCenter, LOADING_SCREEN_SORT_INDEX)

    def end(self):
        self.waitBar.finish()
        self.__active = False
        self.__updateVisibility()
        return (self.__expectedCount, self.__count)

    def abort(self):
        self.__active = False
        self.__updateVisibility()

    def tick(self):
        self.__count = self.__count + 1

    def __updateFill(self):
        now = globalClock.getRealTime()
        dt = now - self.__lastFrameT
        self.__lastFrameT = now
        target = min(self.__count, self.__expectedCount)
        value = self.waitBar['value']
        self.waitBar['value'] = value + (target - value) * (1 - math.exp(-dt * self.FillRate))

    def renderFrame(self):
        self.__updateFill()
        base.graphicsEngine.renderFrame()
