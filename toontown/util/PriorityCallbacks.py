import bisect
import itertools


class PriorityCallbacks:
    """ manage a set of prioritized callbacks, and allow them to be invoked in order of priority """
    _tokens = itertools.count()

    def __init__(self):
        self._callbacks = []

    @staticmethod
    def GetToken():
        return next(PriorityCallbacks._tokens)

    def clear(self):
        while self._callbacks:
            self._callbacks.pop()

    def add(self, callback, priority=None):
        if priority is None:
            priority = 0
        item = (priority, callback)
        bisect.insort(self._callbacks, item)
        return item

    def remove(self, item):
        if item in self._callbacks:
            self._callbacks.remove(item)

    def __call__(self):
        for priority, callback in self._callbacks:
            callback()
