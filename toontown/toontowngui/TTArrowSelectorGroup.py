from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify


class TTArrowSelectorGroup(DirectObject):
    """
    Implements basic hooks for an arrow selector but will not create the direct gui elements, it is left to the
     programmer to make these elements and supply them to the initializer
    """
    notify = directNotify.newCategory('TTArrowSelectorGroup')

    def __init__(self, lArrow, rArrow, label, callback=None, items=None, initIndex=0):
        DirectObject.__init__(self)
        self.lArrow = lArrow
        self.rArrow = rArrow
        self.label = label
        self.items = items
        self.index = initIndex
        self.callback = callback
        self.lArrow['command'] = self.__handleLArrowClicked
        self.rArrow['command'] = self.__handleRArrowClicked
        self.update()

    def destroy(self):
        """
        Does not destroy arrows or label, only de-references them
        """
        self.lArrow['command'] = None
        self.rArrow['command'] = None
        self.lArrow = None
        self.rArrow = None
        self.label = None
        self.items = None

    def enable(self):
        self.lArrow.enable()
        self.rArrow.enable()

    def disable(self):
        self.lArrow.disable()
        self.rArrow.disable()

    def hide(self):
        self.lArrow.hide()
        self.rArrow.hide()
        self.label.hide()

    def show(self):
        self.lArrow.show()
        self.rArrow.show()
        self.label.show()

    def setItems(self, items):
        self.items = items
        self.update()

    def setIndex(self, index):
        self.index = index
        self.update()

    def update(self):
        if self.items is None:
            self.disable()
        elif len(self.items) == 0:
            # Empty items, disable
            self.disable()
        else:
            if self.index == 0:
                # Can't go left
                self.lArrow.disable()
            else:
                self.lArrow.enable()
            if self.index >= len(self.items) - 1:
                # Can't go right
                self.rArrow.disable()
            else:
                self.rArrow.enable()

    def __handleLArrowClicked(self):
        if self.items is None:
            return
        if self.index > 0:
            self.index -= 1
            val = self.items[self.index]
            self.label['text'] = val
            if self.callback:
                self.callback(val)

    def __handleRArrowClicked(self):
        if self.items is None:
            return
        if self.index < len(self.items) - 1:
            self.index += 1
            val = self.items[self.index]
            self.label['text'] = val
            if self.callback:
                self.callback(val)
