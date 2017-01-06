from direct.stdpy import threading


# thread module causes GC errors so I have to do this. :(

class ThreadedCall(threading.Thread):
    def __init__(self, func, args=None, callback=None, callbackArgs=()):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.callback = callback
        self.callbackArgs = callbackArgs

    def run(self):
        if self.args:
            ret = self.func(*self.args)
        else:
            ret = self.func()
        if self.callback:
            if self.callbackArgs:
                self.callback(ret, *self.callbackArgs)
                return
            self.callback(ret)
