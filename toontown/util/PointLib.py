from panda3d.core import Point3
import math


def pointBetween(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    def addDiv(s1, s2):
        return (s1 + s2) / 2

    return Point3(addDiv(x1, x2), addDiv(y1, y2), addDiv(z1, z2))


def distanceBetween(p1, p2):
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    def subSqr(s1, s2):
        return (s1-s2) ** 2

    return math.sqrt(subSqr(x1, x2) + subSqr(y1, y2) + subSqr(z1, z2))
