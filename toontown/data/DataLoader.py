import xml.etree.cElementTree as ET
from panda3d.core import VBase4, VBase3


class DataLoader:
    def __init__(self, path):
        self.path = path

    def loadData(self):
        # Read data from file
        data = []
        root = ET.parse(self.path).getroot()
        items = root.findall('Item')
        for item in items:
            e = {}
            e.update(dict(item.attrib))
            for attr in item:
                try:
                    e.update({attr.tag: attr.attrib['value']})
                except KeyError:
                    raise KeyError('Attribute %s has no value' % attr.tag)
            data.append(e)
        return data


class ModelDataLoader(DataLoader):
    def loadData(self):
        # Read data from file
        data = []
        root = ET.parse(self.path).getroot()
        items = root.findall('Item')
        for item in items:
            e = {}
            e.update(dict(item.attrib))
            for attr in item:
                if attr.tag == 'anims':
                    anims = {}
                    for anim in attr:
                        anims.update({anim.tag: anim.attrib['value']})
                    e.update({attr.tag: anims})
                elif attr.tag == 'color':
                    color = VBase4(1, 1, 1, 1)
                    for c in attr:
                        if c.tag == 'r':
                            color[0] = float(c.attrib['value'])
                        elif c.tag == 'g':
                            color[1] = float(c.attrib['value'])
                        elif c.tag == 'b':
                            color[2] = float(c.attrib['value'])
                        elif c.tag == 'a':
                            color[3] = float(c.attrib['value'])
                    e.update({attr.tag: color})
                elif attr.tag == 'events':
                    events = []
                    for event in attr:
                        events.append([event.attrib['event'], event.attrib['action'], event.attrib['arg']])
                    e.update({attr.tag: events})
                else:
                    try:
                        e.update({attr.tag: attr.attrib['value']})
                    except KeyError:
                        raise KeyError('Attribute %s has no value' % attr.tag)

            data.append(e)
        return data


class IconDataLoader(DataLoader):
    def loadData(self):
        # Read data from file
        data = []
        root = ET.parse(self.path).getroot()
        items = root.findall('Item')
        for item in items:
            e = {}
            e.update(dict(item.attrib))
            for attr in item:
                if attr.tag == 'color':
                    color = VBase4(1, 1, 1, 1)
                    for c in attr:
                        if c.tag == 'r':
                            color[0] = float(c.attrib['value'])
                        elif c.tag == 'g':
                            color[1] = float(c.attrib['value'])
                        elif c.tag == 'b':
                            color[2] = float(c.attrib['value'])
                        elif c.tag == 'a':
                            color[3] = float(c.attrib['value'])
                    e.update({attr.tag: color})
                elif attr.tag == 'pos':
                    pos = VBase3(1, 1, 1)
                    for c in attr:
                        if c.tag == 'x':
                            pos[0] = float(c.attrib['value'])
                        elif c.tag == 'y':
                            pos[1] = float(c.attrib['value'])
                        elif c.tag == 'z':
                            pos[2] = float(c.attrib['value'])
                    e.update({attr.tag: pos})
                else:
                    try:
                        e.update({attr.tag: attr.attrib['value']})
                    except KeyError:
                        raise KeyError('Attribute %s has no value' % attr.tag)

            data.append(e)
        return data


class SuitAttackDataLoader(DataLoader):
    def loadData(self):
        # Read data from file
        data = []
        root = ET.parse(self.path).getroot()
        items = root.findall('Item')
        for item in items:
            e = {}
            e.update(dict(item.attrib))
            for attr in item:
                if attr.tag == 'taunts':
                    taunts = []
                    for taunt in attr:
                        taunts.append(taunt.attrib['value'])
                    e.update({attr.tag: taunts})
                else:
                    try:
                        e.update({attr.tag: attr.attrib['value']})
                    except KeyError:
                        raise KeyError('Attribute %s has no value' % attr.tag)
            data.append(e)
        return data
