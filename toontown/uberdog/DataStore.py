from direct.directnotify import DirectNotifyGlobal
from direct.task import Task
import pickle
import os
import sys

class DataStore:
    QueryTypes = []
    QueryTypes = dict(list(zip(QueryTypes, list(range(len(QueryTypes))))))

    @classmethod
    def addQueryTypes(cls, typeStrings):
        superTypes = list(zip(list(cls.QueryTypes.values()), list(cls.QueryTypes.keys())))
        superTypes.sort()
        newTypes = [ item[1] for item in superTypes ] + typeStrings
        newTypes = dict(list(zip(newTypes, list(range(1 + len(newTypes))))))
        return newTypes

    notify = DirectNotifyGlobal.directNotify.newCategory('DataStore')

    def __init__(self, filepath, writePeriod = 300, writeCountTrigger = 100):
        self.filepath = filepath
        self.writePeriod = writePeriod
        self.writeCountTrigger = writeCountTrigger
        self.writeCount = 0
        self.data = None
        self.className = self.__class__.__name__
        self.open()

    def readDataFromFile(self):
        try:
            file = open(self.filepath + '.bu', 'rb')
            self.notify.debug('Opening backup pickle data file at %s.' % (self.filepath + '.bu',))
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
        except IOError:
            try:
                file = open(self.filepath, 'rb')
                self.notify.debug('Opening old pickle data file at %s..' % (self.filepath,))
            except IOError:
                file = None
                self.notify.debug('New pickle data file will be written to %s.' % (self.filepath,))

        if file:
            data = pickle.load(file)
            file.close()
            self.data = data
        else:
            self.data = {}

    def writeDataToFile(self):
        if self.data is not None:
            self.notify.debug('Data is now synced with disk at %s' % self.filepath)
            try:
                backuppath = self.filepath + '.bu'
                if os.path.exists(self.filepath):
                    os.rename(self.filepath, backuppath)
                outfile = open(self.filepath, 'wb')
                pickle.dump(self.data, outfile)
                outfile.close()
                if os.path.exists(backuppath):
                    os.remove(backuppath)
            except EnvironmentError:
                self.notify.warning(str(sys.exc_info()[1]))

        else:
            self.notify.warning('No data to write. Aborting sync.')

    def syncTask(self, task):
        task.timeElapsed += globalClock.getDt()
        if task.timeElapsed > self.writePeriod:
            if self.writeCount:
                self.writeDataToFile()
                self.resetWriteCount()
            task.timeElapsed = 0.0
        if self.writeCount > self.writeCountTrigger:
            self.writeDataToFile()
            self.resetWriteCount()
            task.timeElapsed = 0.0
        return Task.cont

    def incrementWriteCount(self):
        self.writeCount += 1

    def resetWriteCount(self):
        self.writeCount = 0

    def close(self):
        if self.data is not None:
            self.writeDataToFile()
            taskMgr.remove('%s-syncTask' % (self.className,))
            self.data = None
        return

    def open(self):
        self.close()
        self.readDataFromFile()
        self.resetWriteCount()
        taskMgr.remove('%s-syncTask' % (self.className,))
        t = taskMgr.add(self.syncTask, '%s-syncTask' % (self.className,))
        t.timeElapsed = 0.0

    def reset(self):
        self.destroy()
        self.open()

    def destroy(self):
        self.close()
        if os.path.exists(self.filepath + '.bu'):
            os.remove(self.filepath + '.bu')
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def query(self, query):
        if self.data is not None:
            qData = pickle.loads(query)
            results = self.handleQuery(qData)
            qResults = pickle.dumps(results)
        else:
            results = None
            qResults = pickle.dumps(results)
        return qResults

    def handleQuery(self, query):
        results = None
        return results
