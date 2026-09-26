from panda3d.core import DecalEffect, DepthBiasAttrib, LVector4f

DecalBias = DepthBiasAttrib.make(0, -4, 0)

def biasDecals(nodePath):
    for node in nodePath.findAllMatches('**'):
        if node.node().getEffect(DecalEffect.getClassType()):
            for child in node.getChildren():
                child.setAttrib(DecalBias)

def dgiExtractString8(dgi):
    return dgi.extractBytes(dgi.getUint8()).decode('utf-8')

def dgiExtractColor(dgi):
    a, b, c, d = (dgi.getUint8() / 255.0 for _ in range(4))
    return LVector4f(a, b, c, d)

