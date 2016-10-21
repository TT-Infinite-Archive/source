from toontown.town import Street
from direct.gui import DirectGui
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

class OZStreet(Street.Street):
    def enter(self, requestStatus, visibilityFlag = 1, arrowsOn = 1):
        Street.Street.enter(self, requestStatus, visibilityFlag, arrowsOn)
        print self.zone
        if (self.zone == 6100):
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

    def exit(self, visibilityFlag = 1):
        Street.Street.exit(self, visibilityFlag)

        #todo: cleanup