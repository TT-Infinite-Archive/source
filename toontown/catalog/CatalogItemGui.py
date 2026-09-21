from panda3d.core import NodePath
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import DirectLabel
from direct.interval.IntervalGlobal import ActorInterval, Func, Sequence, Wait
from direct.showbase.PythonUtil import Functor
from otp.avatar import Emote
from toontown.estate import DistributedToonStatuary, GardenTutorial
from toontown.pets import Pet, PetDNA, PetTricks
from toontown.toon import Toon, ToonDNA, ToonHead
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui import TTDialog
from . import CatalogAccessoryItem, CatalogAtticItem, CatalogChatItem, CatalogChatItemPicker
from . import CatalogGardenStarterItem, CatalogItem, CatalogRentalItem
from .CatalogClothingItem import CatalogClothingItem, ClothingTypes, CTString
from .CatalogEmoteItem import CatalogEmoteItem
from .CatalogNametagItem import CatalogNametagItem
from .CatalogPetTrickItem import CatalogPetTrickItem
from .CatalogToonStatueItem import CatalogToonStatueItem


def getClothingPicture(item, avatar):
    item.hasPicture = True
    dna = ToonDNA.ToonDNA(type='t', dna=avatar.style)
    str = ClothingTypes[item.clothingType][CTString]
    if item.isShirt():
        defn = ToonDNA.ShirtStyles[str]
        dna.topTex = defn[0]
        dna.topTexColor = defn[2][item.colorIndex][0]
        dna.sleeveTex = defn[1]
        dna.sleeveTexColor = defn[2][item.colorIndex][1]
        pieceNames = ('**/1000/**/torso-top', '**/1000/**/sleeves')
    else:
        defn = ToonDNA.BottomStyles[str]
        dna.botTex = defn[0]
        dna.botTexColor = defn[1][item.colorIndex]
        pieceNames = ('**/1000/**/torso-bot',)
    toon = Toon.Toon()
    toon.setDNA(dna)
    model = NodePath('clothing')
    for name in pieceNames:
        for piece in toon.findAllMatches(name):
            piece.wrtReparentTo(model)

    model.setH(180)
    toon.delete()
    return item.makeFrameModel(model)


def getEmotePicture(item, avatar):
    item.hasPicture = True
    if item.emoteIndex in Emote.globalEmote.getHeadEmotes():
        toon = ToonHead.ToonHead()
        toon.setupHead(avatar.style, forGui=1)
    else:
        toon = Toon.Toon()
        toon.setDNA(avatar.style)
        toon.loop('neutral')
    toon.setH(180)
    model, ival = item.makeFrameModel(toon, 0)
    track, duration = Emote.globalEmote.doEmote(toon, item.emoteIndex, volume=item.volume)
    if duration == None:
        duration = 0
    name = 'emote-item-%s' % item.sequenceNumber
    CatalogEmoteItem.sequenceNumber += 1
    if track != None:
        track = Sequence(Sequence(track, duration=0), Wait(duration + 2), name=name)
    else:
        track = Sequence(Func(Emote.globalEmote.doEmote, toon, item.emoteIndex), Wait(duration + 4), name=name)
    item.pictureToon = toon
    return (model, track)


def changeEmoteIval(item, volume):
    item.volume = volume
    if not hasattr(item, 'pictureToon'):
        return Sequence()
    track, duration = Emote.globalEmote.doEmote(item.pictureToon, item.emoteIndex, volume=item.volume)
    if duration == None:
        duration = 0
    name = 'emote-item-%s' % item.sequenceNumber
    CatalogEmoteItem.sequenceNumber += 1
    if track != None:
        track = Sequence(Sequence(track, duration=0), Wait(duration + 2), name=name)
    else:
        track = Sequence(Func(Emote.globalEmote.doEmote, item.pictureToon, item.emoteIndex), Wait(duration + 4), name=name)
    return track


def getPetTrickPicture(item, avatar):
    if not hasattr(avatar, 'petDNA'):
        return None, None
    pet = Pet.Pet(forGui=1)
    dna = avatar.petDNA
    if dna == None:
        dna = PetDNA.getRandomPetDNA()
    pet.setDNA(dna)
    pet.setH(180)
    model, ival = item.makeFrameModel(pet, 0)
    pet.setScale(2.0)
    pet.setP(-40)
    track = PetTricks.getTrickIval(pet, item.trickId)
    name = 'petTrick-item-%s' % item.sequenceNumber
    CatalogPetTrickItem.sequenceNumber += 1
    if track != None:
        track = Sequence(Sequence(track), ActorInterval(pet, 'neutral', duration=2), name=name)
    else:
        pet.animFSM.request('neutral')
        track = Sequence(Wait(4), name=name)
    item.petPicture = pet
    item.hasPicture = True
    return (model, track)


def getToonStatuePicture(item, avatar):
    toonStatuary = DistributedToonStatuary.DistributedToonStatuary(None)
    toonStatuary.setupStoneToon(base.localAvatar.style)
    toonStatuary.poseToonFromSpecialsIndex(item.gardenIndex)
    toonStatuary.toon.setZ(0)
    model, ival = item.makeFrameModel(toonStatuary.toon, 1)
    item.pictureToonStatue = toonStatuary
    item.hasPicture = True
    return (model, ival)


def getNametagPicture(item, avatar):
    frame = item.makeFrame()
    inFont = ToontownGlobals.getNametagFont(item.nametagStyle)
    DirectLabel(parent=frame, relief=None, pos=(0, 0, 0.24), scale=0.5, text=base.localAvatar.getName(), text_fg=(1.0, 1.0, 1.0, 1), text_shadow=(0, 0, 0, 1), text_font=inFont, text_wordwrap=9)
    item.hasPicture = True
    return (frame, None)


def requestAccessoryPurchase(catalogItem, phone, callback):
    avatar = base.localAvatar
    accessoriesOnOrder = 0
    for item in avatar.onOrder + avatar.mailboxContents:
        if item.storedInTrunk():
            accessoriesOnOrder += 1

    if avatar.isTrunkFull(accessoriesOnOrder):
        requestPurchaseCleanup(catalogItem)
        buttonCallback = Functor(handleFullPurchaseDialog, catalogItem, phone, callback)
        if avatar.getMaxAccessories() == 0:
            text = TTLocalizer.CatalogPurchaseNoTrunk
        else:
            text = TTLocalizer.CatalogPurchaseTrunkFull
        catalogItem.dialog = TTDialog.TTDialog(style=TTDialog.YesNo, text=text, text_wordwrap=15, command=buttonCallback)
        catalogItem.dialog.show()
    else:
        CatalogItem.CatalogItem.requestPurchase(catalogItem, phone, callback)


def requestAtticPurchase(catalogItem, phone, callback):
    avatar = base.localAvatar
    itemsOnOrder = 0
    for item in avatar.onOrder + avatar.mailboxContents:
        if item.storedInAttic() and not item.replacesExisting():
            itemsOnOrder += 1

    numHouseItems = phone.numHouseItems + itemsOnOrder
    if numHouseItems >= ToontownGlobals.MaxHouseItems and not catalogItem.replacesExisting():
        requestPurchaseCleanup(catalogItem)
        buttonCallback = Functor(handleFullPurchaseDialog, catalogItem, phone, callback)
        catalogItem.dialog = TTDialog.TTDialog(style=TTDialog.YesNo, text=TTLocalizer.CatalogPurchaseHouseFull, text_wordwrap=15, command=buttonCallback)
        catalogItem.dialog.show()
    else:
        CatalogItem.CatalogItem.requestPurchase(catalogItem, phone, callback)


def requestClothingPurchase(catalogItem, phone, callback):
    avatar = base.localAvatar
    clothesOnOrder = 0
    for item in avatar.onOrder + avatar.mailboxContents:
        if item.storedInCloset():
            clothesOnOrder += 1

    if avatar.isClosetFull(clothesOnOrder):
        requestPurchaseCleanup(catalogItem)
        buttonCallback = Functor(handleFullPurchaseDialog, catalogItem, phone, callback)
        catalogItem.dialog = TTDialog.TTDialog(style=TTDialog.YesNo, text=TTLocalizer.CatalogPurchaseClosetFull, text_wordwrap=15, command=buttonCallback)
        catalogItem.dialog.show()
    else:
        CatalogItem.CatalogItem.requestPurchase(catalogItem, phone, callback)


def handleFullPurchaseDialog(catalogItem, phone, callback, buttonValue):
    requestPurchaseCleanup(catalogItem)
    if buttonValue == DGG.DIALOG_OK:
        CatalogItem.CatalogItem.requestPurchase(catalogItem, phone, callback)
    else:
        callback(ToontownGlobals.P_UserCancelled, catalogItem)


def acceptChatItem(catalogItem, mailbox, index, callback):
    if len(base.localAvatar.customMessages) < ToontownGlobals.MaxCustomMessages:
        mailbox.acceptItem(catalogItem, index, callback)
    else:
        showMessagePickerOnAccept(catalogItem, mailbox, index, callback)


def requestChatItemPurchase(catalogItem, phone, callback):
    if len(base.localAvatar.customMessages) < ToontownGlobals.MaxCustomMessages:
        CatalogItem.CatalogItem.requestPurchase(catalogItem, phone, callback)
    else:
        showMessagePicker(catalogItem, phone, callback)


def showMessagePicker(catalogItem, phone, callback):
    catalogItem.phone = phone
    catalogItem.callback = callback
    catalogItem.messagePicker = CatalogChatItemPicker.CatalogChatItemPicker(Functor(handlePickerDone, catalogItem), catalogItem.customIndex)
    catalogItem.messagePicker.show()


def showMessagePickerOnAccept(catalogItem, mailbox, index, callback):
    catalogItem.mailbox = mailbox
    catalogItem.callback = callback
    catalogItem.index = index
    catalogItem.messagePicker = CatalogChatItemPicker.CatalogChatItemPicker(Functor(handlePickerOnAccept, catalogItem), catalogItem.customIndex)
    catalogItem.messagePicker.show()


def handlePickerOnAccept(catalogItem, status, pickedMessage = None):
    print('Picker Status%s' % status)
    if status == 'pick':
        catalogItem.mailbox.acceptItem(catalogItem, catalogItem.index, catalogItem.callback, pickedMessage)
    else:
        catalogItem.callback(ToontownGlobals.P_UserCancelled, None, catalogItem.index)
    catalogItem.messagePicker.hide()
    catalogItem.messagePicker.destroy()
    del catalogItem.messagePicker
    del catalogItem.callback
    del catalogItem.mailbox


def handlePickerDone(catalogItem, status, pickedMessage = None):
    if status == 'pick':
        CatalogItem.CatalogItem.requestPurchase(catalogItem, catalogItem.phone, catalogItem.callback, pickedMessage)
    catalogItem.messagePicker.hide()
    catalogItem.messagePicker.destroy()
    del catalogItem.messagePicker
    del catalogItem.callback
    del catalogItem.phone


def acceptRentalItem(catalogItem, mailbox, index, callback):
    catalogItem.confirmRent = TTDialog.TTGlobalDialog(doneEvent='confirmRent', message=TTLocalizer.MessageConfirmRent, command=Functor(handleRentConfirm, catalogItem, mailbox, index, callback), style=TTDialog.TwoChoice)
    catalogItem.confirmRent.show()


def handleRentConfirm(catalogItem, mailbox, index, callback, choice):
    if choice > 0:
        mailbox.acceptItem(catalogItem, index, callback)
    else:
        callback(ToontownGlobals.P_UserCancelled, catalogItem, index)
    if catalogItem.confirmRent:
        catalogItem.confirmRent.cleanup()
        catalogItem.confirmRent = None


def acceptGardenStarterItem(catalogItem, mailbox, index, callback):
    catalogItem.confirmGarden = TTDialog.TTGlobalDialog(doneEvent='confirmGarden', message=TTLocalizer.MessageConfirmGarden, command=Functor(handleGardenConfirm, catalogItem, mailbox, index, callback), style=TTDialog.TwoChoice)
    catalogItem.confirmGarden.show()


def handleGardenConfirm(catalogItem, mailbox, index, callback, choice):
    if choice > 0:

        def handleTutorialDone():
            catalogItem.gardenTutorial.destroy()
            catalogItem.gardenTutorial = None

        catalogItem.gardenTutorial = GardenTutorial.GardenTutorial(callback=handleTutorialDone)
        if hasattr(mailbox, 'mailboxGui') and mailbox.mailboxGui:
            mailbox.acceptItem(catalogItem, index, callback)
            mailbox.mailboxGui.justExit()
    else:
        callback(ToontownGlobals.P_UserCancelled, catalogItem, index)
    if catalogItem.confirmGarden:
        catalogItem.confirmGarden.cleanup()
        catalogItem.confirmGarden = None


Pictures = {
    CatalogClothingItem: getClothingPicture,
    CatalogEmoteItem: getEmotePicture,
    CatalogNametagItem: getNametagPicture,
    CatalogPetTrickItem: getPetTrickPicture,
    CatalogToonStatueItem: getToonStatuePicture,
}


Purchases = {
    CatalogAccessoryItem.CatalogAccessoryItem: requestAccessoryPurchase,
    CatalogAtticItem.CatalogAtticItem: requestAtticPurchase,
    CatalogChatItem.CatalogChatItem: requestChatItemPurchase,
    CatalogClothingItem: requestClothingPurchase,
}

Accepts = {
    CatalogChatItem.CatalogChatItem: acceptChatItem,
    CatalogGardenStarterItem.CatalogGardenStarterItem: acceptGardenStarterItem,
    CatalogRentalItem.CatalogRentalItem: acceptRentalItem,
}


def handlerFor(table, item):
    for cls in type(item).__mro__:
        if cls in table:
            return table[cls]

    return None


def getPicture(item, avatar):
    handler = handlerFor(Pictures, item)
    if handler:
        return handler(item, avatar)

    return item.getPicture(avatar)


def requestPurchase(catalogItem, phone, callback):
    handler = handlerFor(Purchases, catalogItem)
    if handler:
        return handler(catalogItem, phone, callback)

    catalogItem.requestPurchase(phone, callback)


def requestPurchaseCleanup(catalogItem):
    if hasattr(catalogItem, 'dialog'):
        catalogItem.dialog.cleanup()
        del catalogItem.dialog


def acceptItem(catalogItem, mailbox, index, callback):
    handler = handlerFor(Accepts, catalogItem)
    if handler:
        return handler(catalogItem, mailbox, index, callback)

    catalogItem.acceptItem(mailbox, index, callback)
