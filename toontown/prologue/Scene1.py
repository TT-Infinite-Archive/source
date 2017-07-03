from toontown.prologue.CutsceneHandler import CutsceneHandler
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func


class Scene1(CutsceneHandler):
    SHOW = ['flippy']
    # HIDE = ['philipCog', 'popcornCart', 'bossCrate']

    def getSequence(self):
        moochtopher = self.assets.actorPool.get('moochtopher')

        # Give him a clipboard
        # rightHand = moochtopher.find('**/rightHand')
        # clipBoard = self.assets.propPool.get('clipboard')
        # clipBoard.reparentTo(rightHand)
        # clipBoard.setH(180)
        # clipBoard.setPos(0, 0, 0)
        # clipBoard.setScale(1)

        surlee = self.assets.actorPool.get('surlee')
        gideon = self.assets.actorPool.get('gideon')
        flippy = self.assets.actorPool.get('flippy')
        randomNpc1 = self.assets.actorPool.get('randomNpc1')
        randomNpc2 = self.assets.actorPool.get('randomNpc2')
        philip = self.assets.actorPool.get('philip')

        return Sequence(
            # self.playMusic('Ambience', looping=0, volume=0.8),
            Parallel(
                self.say(flippy, "Welcome to the annual Toontown Science Fair!", 6),
                flippy.actorInterval('wave'),
                Func(flippy.loop, 'neutral')),
            self.say(flippy, "In a few minutes, watch Doctor Surlee launch the very first Toon Rocket into space!", 10),
            self.say(flippy, "You won't want to miss it!", 6),
        )
