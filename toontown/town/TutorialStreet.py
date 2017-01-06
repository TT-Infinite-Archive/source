from toontown.town.TTStreet import TTStreet


class TutorialStreet(TTStreet):
    def enter(self, requestStatus):
        TTStreet.enter(self, requestStatus, visibilityFlag=0, arrowsOn=0)

    def exit(self):
        TTStreet.exit(self, visibilityFlag=0)

    def enterTownBattle(self, event):
        self.loader.townBattle.enter(event, self.fsm.getStateNamed('battle'), tutorialFlag=1)

    def handleEnterTunnel(self, requestStatus, collEntry):
        messenger.send('stopTutorial')
        TTStreet.handleEnterTunnel(self, requestStatus, collEntry)

    def exitDoorIn(self):
        base.localAvatar.obscureMoveFurnitureButton(-1)
