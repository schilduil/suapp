#!/usr/bin/env python3

import pytest

from collections import OrderedDict
import logging
import logging.handlers
import os
import os.path
import re
import sys

sys.path.append(os.getcwd())
from suapp.logdecorator import *


"""
Tests the logdecorator loguse.
"""

# Some classes and functions we're testing with.

class MyClass():
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

class SubMyClass(MyClass):

    @loguse
    def __init__(self, name):
        """Initialize the name of the test class."""
        super(SubMyClass, self).__init__(name)

    @loguse
    def close(self):
        """Closes the test class."""
        logging.getLogger(__name__).info("Closing %s" % (self.name))

@loguse
def my_function1(message):
    logging.getLogger(__name__).warn("Starting %s" % (message))
    return SubMyClass(message)

@loguse(1)  # Don't log the variable with index 1 (i.e. two)
def my_function2(one, two):
    logging.getLogger(__name__).warn("The previous line didn't log 'two', but did log 'one'")
    return "three"

@loguse('a')  # Don't log the named argument 'a'
def my_function3(a, b, g):
    logging.getLogger(__name__).warn("The previous line didn't log 'a', but did log 'b' and 'g'.")
    return "abg"

@loguse('@')  # Don't log the return value.
def my_function4(one, two):
    logging.getLogger(__name__).warn("The previous line logged 'one' and 'two' but the next will not log the return value.")
    return "three"

def test_timings():
    """ Testing the two timings functions. """
    from suapp.logdecorator import add_timing
    init_timings()
    add_timing("f1", 3)
    add_timing("f2", 4.234)
    add_timing("f1", 6)
    add_timing("f3", 6.2524)
    add_timing("f2", 7.5234)
    add_timing("f2", 8.70987)
    add_timing("f2", 9.78034970)
    timings = get_timings()
    print(timings)
    report = timings_report()
    print(report)
    assert report == OrderedDict([('f2', (4, 30.2476197, 7.561904925)), ('f3', (1, 6.2524, 6.2524)), ('f1', (2, 9, 4.5))])

def test_timings_disabled():
    """ Testing the two timings functions when they should do nothing. """
    from suapp.logdecorator import add_timing
    disable_timings()
    add_timing("f1", 3)
    add_timing("f2", 4.234)
    add_timing("f1", 6)
    add_timing("f3", 6.2524)
    add_timing("f2", 7.5234)
    add_timing("f2", 8.70987)
    add_timing("f2", 9.78034970)
    timings = get_timings()
    print(timings)
    report = timings_report()
    print(report)
    assert report == None

@pytest.fixture
def memory_logger():
    """ Test fixture to set the handler to a memory buffer """
    # Huge capacity and NEVER flush.
    capacity = 10**6
    flushLevel=255
    if sys.version_info >= (3,6):
        handler = logging.handlers.MemoryHandler(capacity, flushLevel, target=None, flushOnClose=False)
    else:
        handler = logging.handlers.MemoryHandler(capacity, flushLevel, target=None)
    logger = logging.getLogger()
    # Cleaning up, just to be sure.
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.addHandler(handler)
    return (logger, handler)

def test_logging_info(memory_logger):
    """ Test the logging with loglevel=INFO """
    (logger, handler) = memory_logger
    logger.setLevel(logging.INFO)
    x = my_function1("Hello World!")
    x.lock()
    x.unlock()
    x.close()
    my_function2("First variable", "Second variable")
    my_function3(a="alpha", b="beta", g="gamma")
    my_function4(one=1, two=2)

    # fields = ['created', 'exc_info', 'exc_text', 'filename', 'funcName', 'getMessage', 'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName']
    fields = ['levelno', 'levelname', 'name', 'filename', 'module', 'funcName', 'msg']
    expected = [
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function1 Starting Hello World!" % (logging.WARNING, __name__),
        "%s INFO %s test_logdecorator.py test_logdecorator lock Locking Hello World!" % (logging.INFO, __name__),
        "%s INFO %s test_logdecorator.py test_logdecorator unlock Unlocking Hello World!" % (logging.INFO, __name__),
        "%s INFO %s test_logdecorator.py test_logdecorator close Closing Hello World!" % (logging.INFO, __name__),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function2 The previous line didn't log 'two', but did log 'one'" % (logging.WARNING, __name__),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function3 The previous line didn't log 'a', but did log 'b' and 'g'." % (logging.WARNING, __name__),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function4 The previous line logged 'one' and 'two' but the next will not log the return value." % (logging.WARNING, __name__),
    ]
    assert len(handler.buffer) == len(expected)
    for logline, expected in zip(handler.buffer,expected):
        line = []
        for field in fields:
            # We substitute any hex strings with 0x000000000000
            line.append(re.sub('0x[0-9a-f]*', '0x000000000000', str(getattr(logline, field))))
        assert " ".join(line) == expected

def test_logging_debug(memory_logger):
    """ Test the logging with loglevel=DEBUG """
    (logger, handler) = memory_logger
    logger.setLevel(logging.DEBUG)
    x = my_function1("The end of the World is near!")
    x.lock()
    x.unlock()
    x.close()
    my_function2("First variable", "Second variable")
    my_function3(a="alpha", b="beta", g="gamma")
    my_function4(one=1, two=2)

    fields = ['levelno', 'levelname', 'name', 'filename', 'module', 'funcName']
    expected = [
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function1(('The end of the World is near!',), {})" % (logging.DEBUG),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function1 Starting The end of the World is near!" % (logging.WARNING, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > SubMyClass.__init__((<test_logdecorator.SubMyClass object at 0x000000000000>, 'The end of the World is near!'), {})" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > MyClass.__init__((<test_logdecorator.SubMyClass object at 0x000000000000>,), {})" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < MyClass.__init__: None" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < SubMyClass.__init__: None" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < my_function1: <test_logdecorator.SubMyClass object at 0x000000000000>" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > MyClass.lock((<test_logdecorator.SubMyClass object at 0x000000000000>,), {})" % (logging.DEBUG),
        "%s INFO %s test_logdecorator.py test_logdecorator lock Locking The end of the World is near!" % (logging.INFO, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < MyClass.lock: None" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > MyClass.unlock((<test_logdecorator.SubMyClass object at 0x000000000000>,), {})" % (logging.DEBUG),
        "%s INFO %s test_logdecorator.py test_logdecorator unlock Unlocking The end of the World is near!" % (logging.INFO, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < MyClass.unlock: None" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > SubMyClass.close((<test_logdecorator.SubMyClass object at 0x000000000000>,), {})" % (logging.DEBUG),
        "%s INFO %s test_logdecorator.py test_logdecorator close Closing The end of the World is near!" % (logging.INFO, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < SubMyClass.close: None" % (logging.DEBUG),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function2(('First variable',), {})" % (logging.DEBUG),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function2 The previous line didn't log 'two', but did log 'one'" % (logging.WARNING, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < my_function2: 'three'" % (logging.DEBUG),
        (
            "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function3((), {'g': 'gamma', 'b': 'beta'})" % (logging.DEBUG),
            "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function3((), {'b': 'beta', 'g': 'gamma'})" % (logging.DEBUG),
        ),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function3 The previous line didn't log 'a', but did log 'b' and 'g'." % (logging.WARNING, __name__),
        "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator < my_function3: 'abg'" % (logging.DEBUG),
        (
            "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function4((), {'one': 1, 'two': 2})" % (logging.DEBUG),
            "%s DEBUG test_logdecorator logdecorator.py logdecorator decorator > my_function4((), {'two': 2, 'one': 1})" % (logging.DEBUG),
        ),
        "%s WARNING %s test_logdecorator.py test_logdecorator my_function4 The previous line logged 'one' and 'two' but the next will not log the return value." % (logging.WARNING, __name__),
        "%s DEBUG %s logdecorator.py logdecorator decorator < my_function4" % (logging.DEBUG, __name__),
    ]
    assert len(handler.buffer) == len(expected)
    for logline, expected in zip(handler.buffer,expected):
        line = []
        for field in fields:
            # We substitute any hex strings with 0x000000000000
            line.append(re.sub('0x[0-9a-f]*', '0x000000000000', str(getattr(logline, field))))
        line.append(re.sub('0x[0-9a-f]*', '0x000000000000', logline.getMessage()))
        if isinstance(expected, tuple):
            assert " ".join(line) in expected
        else:
            assert " ".join(line) == expected
