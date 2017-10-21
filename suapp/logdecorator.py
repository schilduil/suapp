#!/usr/bin/env python3

"""
Copyright (C), 2013, The Schilduil Team. All rights reserved.
"""
import logging
import inspect
import time
from collections import OrderedDict
from operator import add
from functools import wraps


__all__ = ["logging", "get_timings", "init_timings", "disable_timings", "timings_report", "loguse"]


timings = None


def get_timings():
    """ Returns the gathered timings. """
    return timings

def init_timings():
    """ Initiates/Resets the timings. """
    global timings
    timings = {}

def disable_timings():
    """ Disables the gathering of timings. """
    global timings
    timings = None

def add_timing(f, time):
    """Adds an executing time for a callable to the timings."""
    global timings
    if timings is None:
        return
    if f in timings:
        timings[f] = tuple(map(add, timings[f], (1, time)))
    else:
        timings[f] = (1, time)

def timings_report():
    """Generated a report of the timings of functions.
    The slowest on average will be first."""
    if timings is None:
        return None
    report = {}
    for f, (count, time) in timings.items():
        report[f] = time / count

    sorted_report = OrderedDict()
    for f in sorted(report, key=report.get, reverse=True):
        sorted_report[f] = timings[f] + (report[f],)

    return sorted_report

def loguse(param=None):
    """When in debug it will log entering and exiting a function or object methods.

    WARNING: Some callables are broken when you use this (e.g. Thread.__init__)
    Upon entering the callable it will also log all arguments.

    You can specify arguments to this decorator: a string, an int or a list of
    string and/or integers. A string causes not log that name argument, an int
    causes not to log that positional argument.

    Example:
        @loguse             # will log all arguments.
        @loguse('arg0')     # will log all but not a named argument named 'arg0'.
        @loguse(0)          # will log all but the first positional argument.
        @loguse(['arg0',0]) # will log all but the first pos. and 'arg0'.
    """
    # Checking the param
    #   If it is a callable then just return what real_loguse(f) would return.
    #   If it is a parameter (even if None) return the real_loguse function.
    # Param:
    #   It could be None => empty list
    #   It could be a string => list with that string as element
    #   It could be an iterable => ok
    start_time = time.time()
    start_time_callable = 0
    end_time_callable = 0
    f = None
    ignore_parameters = []
    if param is None:
        ignore_parameters = []
    elif callable(param):
        f = param
    elif isinstance(param, str):
        ignore_parameters = [param]
    elif isinstance(param, int):
        ignore_parameters = [param]
    elif hasattr(param, '__iter__'):
        ignore_parameters = param
    # Looking for the classname.
    classname = "?"
    try:
        # We don't want this weird stuff messing in the log decorator
        # halting our code. And that is a real possibility as this
        # stuff is in CPtython but does not have to present in other
        # python implementation. More info on inspect:
        # http://docs.python.org/3/library/inspect.html
        classname = inspect.getouterframes(inspect.currentframe())[1][3]
    except:
        pass

    def real_loguse(f):
        log = logging.getLogger(f.__module__)

        @wraps(f)
        def decorator(*args, **kwargs):
            l_args = list(args)
            l_kwargs = dict(kwargs)
            if log.isEnabledFor(logging.DEBUG):
                ignore_parameters.sort(key=str, reverse=True)
                if ignore_parameters:
                    # Deleting any parameters so they are not logged.
                    for param in ignore_parameters:
                        if isinstance(param, int):
                            try:
                                l_args.pop(param)
                            except:
                                pass
                        else:
                            try:
                                del l_kwargs[str(param)]
                            except:
                                pass
                if classname == "<module>":
                    log.debug("> %s(%r, %r)", f.__name__, tuple(l_args), l_kwargs)
                else:
                    log.debug("> %s.%s(%r, %r)", classname, f.__name__, tuple(l_args), l_kwargs)
            start_time_callable = time.time()
            result = f(*args, **kwargs)
            end_time_callable = time.time()
            if log.isEnabledFor(logging.DEBUG):
                if '@' in ignore_parameters:
                    if classname == "<module>":
                        log.debug("< %s", f.__name__)
                    else:
                        log.debug("< %s.%s", classname, f.__name__)
                else:
                    if classname == "<module>":
                        log.debug("< %s: %r", f.__name__, result)
                    else:
                        log.debug("< %s.%s: %r", classname, f.__name__, result)
            return result
        return decorator
    end_time = time.time()
    add_timing('loguse overhead', end_time - end_time_callable + start_time_callable - start_time)
    if f:
        add_timing(f, end_time_callable - start_time_callable)
        return real_loguse(f)
    else:
        return real_loguse


if __name__ == "__main__":

    timings = {}

    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.INFO)

    class TestClass():
        """Test class for the logdecorator"""
        name = "APP"

        @loguse(1)  # Don't log the variable with index 1 (i.e. name)
        def __init__(self, name):
            """Initialize the name of the test class."""
            self.name = name

        @loguse
        def lock(self):
            """Locks the test class."""
            logging.getLogger(__name__).info("Locking %s" % (self.name))

        @loguse
        def unlock(self):
            """Unlocks the test class."""
            logging.getLogger(__name__).info("Unlocking %s" % (self.name))

        @loguse
        def close(self):
            """Closes the test class."""
            logging.getLogger(__name__).info("Closing %s" % (self.name))

    class SubTestClass(TestClass):

        @loguse
        def __init__(self, name):
            """Initialize the name of the test class."""
            super(SubTestClass, self).__init__(name)

        @loguse
        def close(self):
            """Closes the test class."""
            logging.getLogger(__name__).info("Closing %s" % (self.name))

    @loguse
    def test1(message):
        logging.getLogger(__name__).warn("Starting %s" % (message))
        return SubTestClass(message)

    @loguse(1)  # Don't log the variable with index 1 (i.e. two)
    def test2(one, two):
        logging.getLogger(__name__).warn("The previous line didn't log 'two', but did log 'one'")

    @loguse('a')  # Don't log the named argument 'a'
    def test3(a, b, g):
        logging.getLogger(__name__).warn("The provious line didn't log 'a', but did log 'b' and 'g'.")

    print("========== INFO ==========")
    x = test1("Hello World!")
    x.lock()
    x.unlock()
    x.close()
    print("%s: %s" % (x.lock.__name__, x.lock.__doc__))
    test2("First variable", "Second variable")
    test3(a="alpha", b="beta", g="gamma")

    print("========== DEBUG ==========")
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    x = test1("The end of the World is near!")
    x.lock()
    x.unlock()
    x.close()
    print("%s: %s" % (x.lock.__name__, x.lock.__doc__))
    test2("First variable", "Second variable")
    test3(a="alpha", b="beta", g="gamma")

    for f, (count, total, avg) in timings_report().items():
        print("%s: %s (%s/%s)" % (f, avg, total, count))
