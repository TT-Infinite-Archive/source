from panda3d.core import TextNode
from toontown.toonbase import ToontownClientGlobals


class CogdoGameMovie:

    def __init__(self):
        self._ival = None
        self._task = None
        return

    def load(self):
        textNode = TextNode('moviedialogue')
        textNode.setTextColor(0, 0, 0, 1)
        textNode.setCardColor(1, 1, 1, 1)
        textNode.setCardAsMargin(0, 0, 0, 0)
        textNode.setCardDecal(True)
        textNode.setWordwrap(27.0)
        textNode.setAlign(TextNode.ACenter)
        textNode.setFont(ToontownClientGlobals.getToonFont())
        self._dialogueLabel = aspect2d.attachNewNode(textNode)
        self._dialogueLabel.setScale(0.06, 0.06, 0.06)
        self._dialogueLabel.setPos(0.32, 0, -0.75)
        self._dialogueLabel.reparentTo(hidden)

    def unload(self):
        if self._ival is not None and self._ival.isPlaying():
            self.finish()
        self._ival = None
        self._dialogueLabel.removeNode()
        del self._dialogueLabel
        return

    def getIval(self):
        return self._ival

    def play(self, elapsedTime = 0.0):
        self._dialogueLabel.reparentTo(aspect2d)
        self._ival.start(elapsedTime)

    def _startUpdateTask(self):
        self._task = taskMgr.add(self._updateTask, 'CogdoGameMovie_updateTask', 45)

    def _stopUpdateTask(self):
        if self._task is not None:
            taskMgr.remove(self._task)
            self._task = None
        return

    def _updateTask(self, task):
        return task.cont

    def end(self):
        self._ival.finish()
