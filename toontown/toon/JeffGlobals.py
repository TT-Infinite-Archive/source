'''
Created on Jul 4, 2017

@author: Drew
'''
from panda3d.core import CardMaker, NodePath



def makeCard(book=False):
    cardMaker = CardMaker('jeff-cm')
    cardMaker.setHasUvs(1)
    cardMaker.setFrame(-0.5, 0.5, -0.5, 0.5)

    nodePath = NodePath('jeff')
    nodePath.setBillboardPointEye()

    jeff = nodePath.attachNewNode(cardMaker.generate())
    jeff.setTexture(loader.loadTexture('phase_3/maps/avatar_pallette_jeff.png'))
    jeff.setY(-0.3)
    jeff.setTransparency(True)

    return nodePath


def addHeadEffect(head, book=False):
    card = makeCard(book=book)
    card.setScale(1.45 if book else 2.5)
    card.setZ(0.05 if book else 0.5)
    for nodePath in head.getChildren():
        nodePath.removeNode()
    card.instanceTo(head)


def addToonEffect(toon):
    toon.getDialogueArray = lambda *args, **kwargs: [loader.loadSfx('phase_3.5/audio/dial/AV_jeff_short.ogg'), 
                                                     loader.loadSfx('phase_3.5/audio/dial/AV_jeff_long.ogg'),
                                                     loader.loadSfx('phase_3.5/audio/dial/AV_jeff_long.ogg'),
                                                     loader.loadSfx('phase_3.5/audio/dial/AV_jeff_short.ogg'),
                                                     loader.loadSfx('phase_3.5/audio/dial/AV_jeff_short.ogg'),
                                                     loader.loadSfx('phase_3.5/audio/dial/AV_jeff_long.ogg')]
    for lod in toon.getLODNames():
        addHeadEffect(toon.getPart('head', lod))
