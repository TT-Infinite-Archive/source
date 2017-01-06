import cProfile
import pstats
import StringIO


# Times how long it takes a function to be called and prints it in a pretty way :)
def timeFunc(func):
    def _decorator(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        x = func(*args, **kwargs)
        pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print s.getvalue()
        return x
    return _decorator