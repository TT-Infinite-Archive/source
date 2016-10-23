from toontown.town import Street
from direct.gui import DirectGui
from pandac.PandaModules import *
from panda3d.core import Fog
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer

class OZStreet(Street.Street):
    def enter(self, requestStatus, visibilityFlag = 1, arrowsOn = 1):
        Street.Street.enter(self, requestStatus, visibilityFlag, arrowsOn)
        if (self.zone == 6100):
            self.enterForest()

    def enterForest(self):
        # Disable time here
        self.disableTimeEffects()

        # Build the tunnel sign
        geom = base.cr.playGame.getPlace().loader.geom
        top = geom.find('**/linktunnel_bosshq_10000_DNARoot')
        sign = top.find('**/Sign_5')
        sign.node().setEffect(DecalEffect.make())
        locator = top.find('**/sign_origin')
        signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.BossbotHQ[-1]),
                                          font=ToontownGlobals.getSuitFont(), scale=TTLocalizer.GZSZLsignText,
                                          fg=(0, 0, 0, 1), mayChange=False, parent=sign)
        signText.setPosHpr(locator, 0, 0, -0.3, 0, 0, 0)
        signText.setDepthWrite(0)

        # Add fog, and stop the sky
        self.fog = Fog('BossbotHQFog')
        self.loader.hood.stopSky()

    def exitForest(self):
        pass

    def setFog(self):
        if base.wantFog:
            self.fog.setColor(0.1, 0.1, 0.1)
            self.fog.setExpDensity(0.004)
            render.clearFog()
            render.setFog(self.fog)
            self.sky.clearFog()
            self.sky.setFog(self.fog)

    def exit(self, visibilityFlag = 1):
        Street.Street.exit(self, visibilityFlag)

        if (self.zone == 6100):
            self.exitForest()