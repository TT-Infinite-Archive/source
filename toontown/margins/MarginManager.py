from panda3d.core import PandaNode

from toontown.margins.MarginCell import MarginCell


class MarginManager(PandaNode):
    def __init__(self):
        PandaNode.__init__(self, 'margins')

        self.cells = set()
        self.visibles = set()

    def addCell(self, x, y, a2dMarker):
        cell = MarginCell()
        cell.reparentTo(a2dMarker)
        cell.setPos(x, 0, y)
        cell.setScale(0.2)
        cell.setActive(True)

        self.cells.add(cell)
        self.reorganize()

        return cell

    def removeCell(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.reorganize()

    def addVisible(self, visible):
        self.visibles.add(visible)
        self.reorganize()

    def removeVisible(self, visible):
        if visible in self.visibles:
            self.visibles.remove(visible)
            self.reorganize()

    def getActiveCells(self):
        return [cell for cell in self.cells if cell.getActive()]

    def chooseCell(self, visible, cells):
        # Prefer the cell nearest to where the visible actually is on screen:
        target = visible.getMarginScreenPos()
        if target is None:
            lastCell = visible.getLastCell()
            return lastCell if lastCell in cells else cells[0]

        return min(
            cells,
            key=lambda cell: (cell.getPos(base.aspect2d).getXz() - target).lengthSquared())

    def reorganize(self):
        # First, get all of the active cells:
        activeCells = self.getActiveCells()

        # Next, get all of the visibles sorted by priority. We can only display
        # so many, so truncate them based on the number of active cells:
        visibles = sorted(
            self.visibles, key=lambda visible: visible.getPriority(),
            reverse=True)[:len(activeCells)]

        # Now, let's build a list of empty cells:
        emptyCells = []
        for cell in activeCells:
            content = cell.getContent()
            if content in visibles:
                # This cell is already displaying something we want to see.
                # Ignore it:
                visibles.remove(content)
                continue
            elif content is not None:
                # This cell isn't displaying anything interesting, so let's
                # empty it:
                cell.setContent(None)
            emptyCells.append(cell)

        # Assign the visibles to their cells:
        for visible in visibles:
            cell = self.chooseCell(visible, emptyCells)
            cell.setContent(visible)
            emptyCells.remove(cell)
