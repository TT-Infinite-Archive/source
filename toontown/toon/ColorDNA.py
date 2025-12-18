from panda3d.core import Datagram, VBase3, VBase4

from direct.distributed.PyDatagram import PyDatagram

import colorsys


def convertToRgb(hue, saturation, value):
    temp = colorsys.hsv_to_rgb(hue, saturation, value)
    return VBase4(temp[0], temp[1], temp[2], 1.0)


def convertToHsv(red, green, blue, alpha=1.0):
    temp = colorsys.rgb_to_hsv(red, green, blue)
    return VBase3(temp[0], temp[1], temp[2])


class PartColorDNA:
    """
    Each toon part (head, arm, leg) has its own DNA object with its own
    HSV values.
    """
    def __init__(self, hue=50.00, saturation=50.00, value=50.00):
        self.hue = round(hue, 2)
        self.saturation = round(saturation, 2)
        self.value = round(value, 2)

    def makeNetString(self, dg):
        dg.addUint16(int(self.hue * 100.0))
        dg.addUint16(int(self.saturation * 100.0))
        dg.addUint16(int(self.value * 100.0))

    def makeFromDatagram(self, dgi):
        self.hue = dgi.getUint16() / 100.0
        self.saturation = dgi.getUint16() / 100.0
        self.value = dgi.getUint16() / 100.0

    def get(self):
        return self.hue, self.saturation, self.value

    def getRgb(self):
        return convertToRgb(self.hue, self.saturation, self.value)

    def reset(self, hue, saturation, value):
        self.hue = round(hue, 2)
        self.saturation = round(saturation, 2)
        self.value = round(value, 2)

    def resetRgb(self, red, green, blue, a=1.0):
        hsv = convertToHsv(red, green, blue)
        self.reset(*hsv)

    def __str__(self):
        return '%s %s %s' % (self.hue, self.saturation, self.value)


class ToonColorDNA:
    """
    This class will be used for a toon's color using HSV color values.
    """
    def __init__(self, headColor=None, armColor=None,
                 legColor=None):

        if headColor is None:
            headColor = PartColorDNA()
        if armColor is None:
            armColor = PartColorDNA()
        if legColor is None:
            legColor = PartColorDNA()

        self.headColor = headColor
        self.armColor = armColor
        self.legColor = legColor
        self.dna = (self.headColor, self.armColor, self.legColor)

    def makeNetString(self):
        dg = PyDatagram()

        for part in self.dna:
            part.makeNetString(dg=dg)

        return dg.getMessage()

    def makeFromDatagram(self, dgi):
        self.headColor.makeFromDatagram(dgi)
        self.armColor.makeFromDatagram(dgi)
        self.legColor.makeFromDatagram(dgi)
        self.dna = (self.headColor, self.armColor, self.legColor)

    def __str__(self):
        retVal = ''

        for part in self.dna:
            retVal += str(part) + ' '

        return retVal
