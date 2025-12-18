from panda3d.core import ConfigVariableInt
import objgraph
import random
import time
from direct.stdpy import threading, thread
from otp.ai.MagicWordGlobal import *
from plotly import plotly
from plotly import graph_objs


def outputLeakingCount():
    roots = objgraph.get_leaking_objects()
    print('Leaking %d objects...' % len(roots))


def outputLeaking():
    roots = objgraph.get_leaking_objects()
    print('Leaking %d objects...' % len(roots))
    objgraph.show_most_common_types(objects=roots)


class LeakGraph(threading.Thread):
    notify = directNotify.newCategory('LeakGraph')
    notify.setInfo(True)

    CHECK_CYCLE = ConfigVariableInt('leak-graph-check-cycle', 3).getValue()
    GRAPH_CYCLE = ConfigVariableInt('leak-graph-graph-cycle', 90).getValue()

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.cycles = 0
        self.colors = []
        self.stats = {}
        self.checkThread = None
        self.graphThread = None
        self.stop = False

    def run(self):
        self.notify.info('Starting check and graph cycles.')
        self.checkThread = thread.start_new_thread(self.checkCycle, ())
        self.graphThread = thread.start_new_thread(self.graphCycle, ())

    def checkCycle(self):
        time.sleep(LeakGraph.CHECK_CYCLE)
        if self.stop:
            return
        self.notify.info('Running check cycle.')
        seconds = self.cycles * LeakGraph.CHECK_CYCLE
        outputLeakingCount()
        leakingObjects = objgraph.typestats()
        for objName, count in list(leakingObjects.items()):
            if count > 100:
                if objName not in self.stats:
                    self.stats[objName] = {}
                self.stats[objName][seconds] = count
        del leakingObjects
        self.cycles += 1
        if not self.stop:
            self.checkCycle()

    def graphCycle(self):
        time.sleep(LeakGraph.GRAPH_CYCLE)
        if self.stop:
            return
        self.notify.info('Running graph cycle.')
        obj2Val = {}
        for objName in self.stats:
            obj2Val[objName] = max(self.stats[objName].values())
        lines = []
        for objName in list(self.stats.keys()):
            colorString = self.generateColor()
            try:
                line = graph_objs.Scatter(
                        x=list(self.stats[objName].keys()),
                        y=list(self.stats[objName].values()),
                        mode='lines',
                        name=objName,
                        line=graph_objs.Line(
                            width=2,
                            color=colorString,
                        ),
                )
                lines.append(line)
            except Exception as e:
                self.notify.warning(e.message)
        data = graph_objs.Data(lines)
        layout = graph_objs.Layout(
            title=self.name,
            xaxis=graph_objs.XAxis(
                title='Time since generate',
            ),
            yaxis=graph_objs.YAxis(
                title='Object count',
            )
        )
        fig = graph_objs.Figure(data=data, layout=layout)
        plotUrl = plotly.plot(fig, filename=self.name, auto_open=False, fileopt='overwrite')
        self.notify.info('Graph saved to: %s' % plotUrl)
        if not self.stop:
            self.graphCycle()

    def generateColor(self):
        rgb = [random.randint(15, 255) for _ in range(3)]
        color = 'rgb' + str(tuple(rgb))
        if color not in self.colors:
            self.colors.append(color)
            return color
        return self.generateColor()

@magicWord(category=CATEGORY_ADMINISTRATOR, types=[])
def stopLeakGraph():
    simbase.air.leakGraph.stop = True
    return 'Stopping LeakGraph at next interval...'
