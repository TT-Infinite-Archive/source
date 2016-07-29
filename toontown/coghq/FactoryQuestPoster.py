from toontown.toonbase.ToontownGlobals import getSuitFont
from direct.gui.DirectGui import DirectWaitBar, DirectFrame, DGG, OnscreenText
from panda3d.core import TransparencyAttrib, CardMaker, NodePath, VBase4
from toontown.toonbase import TTLocalizer
from toontown.coghq import FactoryQuestGlobals
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval


class FactoryQuestPoster(DirectFrame):
    def __init__(self, factory, parent=aspect2d, **kw):
        DirectFrame.__init__(self, parent=parent, relief=None, **kw)
        self.factory = factory

        self.questId = -1
        self.quest = None  # Current Quest object
        self.completed = False
        self.progress = 0
        self.goal = 0

        self.questPoster = None  # Direct Frame: The look of the quest poster
        self.questDescription = None  # Onscreen Text: The description of the current quest
        self.questPosterBar = None  # Direct Wait Bar: Progress of the quest, contains text also
        self.questPosterImage = None  # NodePath: Piplups image for the geom
        self.ignore('stickerBookEntered')
        self.accept('stickerBookEntered', self.hide)
        self.ignore('stickerBookExited')
        self.accept('stickerBookExited', self.show)

    def load(self):
        self.setColorScale(0.0, 0.0, 0.0, 0.0)
        filepath = 'phase_9/maps/factory-quest-poster.png'
        tex = loader.loadTexture(filepath)
        cm = CardMaker(filepath + ' card')
        cm.setFrame(-tex.getOrigFileXSize(), tex.getOrigFileXSize(), -tex.getOrigFileYSize(), tex.getOrigFileYSize())
        self.questPosterImage = NodePath(cm.generate())
        self.questPosterImage.setTexture(tex)
        self.questPosterImage.setBin('background', 98)

        self.questPoster = DirectFrame(parent=self, geom=self.questPosterImage, geom_scale=0.00110, geom_pos=(0.0, 0.0, 0.0), frameSize=(-0.0, 0.0, -0.0, 0.0), frameColor=(1.0, 1.0, 1.0, 1))
        self.questPoster.setTransparency(TransparencyAttrib.MAlpha)
        self.questDescription = OnscreenText(parent=self.questPoster, text='', fg=(1.0, 1.0, 1.0, 0.95), scale=0.04, wordwrap=10, pos=(0.0, 0.09), font=getSuitFont(), shadow=(0.1, 0.1, 0.1, 1), shadowOffset=(0.1, 0.1))
        self.questPosterBar = DirectWaitBar(parent=self.questPoster, text='', text_font=getSuitFont(), text_scale=0.03, text_pos=(0.0, -0.01), pos=(0.0, 0.0, -0.1), value=0, range=1, relief=DGG.FLAT, frameColor=(0.1, 0.1, 0.1, 0.25), barColor=VBase4(0.75, 0.65, 0.65, 0.85), borderWidth=(0.002, 0.001), frameSize=(-0.2, 0.2, -0.022, 0.022))
        self.questPosterBar.setTransparency(TransparencyAttrib.MAlpha)
        Sequence(LerpColorScaleInterval(self, 0.5, (1.0, 1.0, 1.0, 1.0), (0.0, 0.0, 0.0, 0.0), blendType='easeIn')).start()

    def setQuest(self, questId):
        if self.quest is None:
            self.quest = FactoryQuestGlobals.FactoryQuests[questId]
            self.questId = questId

        self.goal = self.quest.goal
        self.progress = 0
        self.completed = False

        questDescription = TTLocalizer.FactoryQuestDescriptions[questId]
        questPosterBarText = str(self.progress)+'/'+str(self.goal)+' '+TTLocalizer.FactoryQuestProgressString[self.questId]
        self.questDescription['text'] = questDescription
        self.questPosterBar['text'] = questPosterBarText
        self.questPosterBar['text_fg'] = (0.0, 0.0, 0.0, 1.0)

    def setProgress(self, progress):
        if self.completed:
            return

        self.progress = progress
        if self.progress >= self.goal:
            self.progress = self.goal
            self.setCompleted()
        else:
            print('Progress is now', self.progress)
            self.completed = False
            self.questPosterBar['text'] = (str(self.progress)+'/'+str(self.goal)+' '+TTLocalizer.FactoryQuestProgressString[self.questId])
            self.questPosterBar['value'] = (float(self.progress)/float(self.goal))
            self.questPosterBar['text_fg'] = (0.0, 0.0, 0.0, 1.0)

    def setCompleted(self):
        # TODO: sound here to notify quest done?
        self.completed = True
        self.questPosterBar['value'] = 1
        self.questPosterBar['text'] = TTLocalizer.QuestsCompleteString
        self.questPosterBar['text_fg'] = VBase4(1.0, 1.0, 1.0, 0.9)


    def destroy(self):
        if self.questPoster:
            self.questPoster.destroy()
            self.questPoster = None
        if self.questDescription:
            self.questDescription.destroy()
            self.questDescription = None
        if self.questPosterBar:
            self.questPosterBar.destroy()
            self.questPosterBar = None
        if self.questPosterImage:
            del self.questPosterImage
        self.factory = None
        self.ignoreAll()
        DirectFrame.destroy(self)
