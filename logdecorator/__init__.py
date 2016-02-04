#!/usr/bin/env python3

"""
Copyright (C), 2013, The Schilduil Team. All rights reserved.
"""
import logging
import inspect
from functools import wraps


def loguse(f):
    """When in debug it will log entering and exiting a function or object methods.

    I don't know yet if it works on other callables.
    """
    log = logging.getLogger(f.__module__)
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
    @wraps(f)
    def decorator(*args, **kwargs):
        if log.isEnabledFor(logging.DEBUG):
            if classname == "<module>":
                log.debug("> %s(%r, %r)" % (f.__name__, args, kwargs))
            else:
                log.debug("> %s.%s(%r, %r)" % (classname, f.__name__, args, kwargs))
        result = f(*args, **kwargs)
        if log.isEnabledFor(logging.DEBUG):
            if classname == "<module>":
                log.debug("< %s: %r" % (f.__name__, result))
            else:
                log.debug("< %s.%s: %r" % (classname, f.__name__, result))
        return result
    return decorator


if __name__ == "__main__":

    logging.basicConfig(format = '%(asctime)s %(levelname)s %(name)s %(message)s', level = logging.DEBUG)

    class TestClass():
        """Test class for the logdecorator"""
        name = "APP"

        @loguse
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

    x = test1("Hello World!")
    x.lock()
    x.unlock()
    x.close()

    print("%s: %s" % (x.lock.__name__, x.lock.__doc__))

    logging.getLogger(__name__).setLevel(logging.INFO)

    x = test1("The end of the World is near!")
    x.lock()
    x.unlock()
    x.close()

    print("%s: %s" % (x.lock.__name__, x.lock.__doc__))


