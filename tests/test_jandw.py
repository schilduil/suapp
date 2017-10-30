#!/usr/bin/env python3

import pytest

import logging
import os
import os.path
import re
import sys

sys.path.append(os.getcwd())
from suapp.jandw import *

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

def test_jandw_flow(memory_logger):
    (logger, handler) = memory_logger
    logger.setLevel(logging.DEBUG)

    class Application(Wooster):
        name = "APP"

        def inflow(self, jeeves, drone):
            self.jeeves = jeeves
            print("""This is the Jeeves and Wooster library!

Jeeves is Wooster's indispensible valet: a gentleman's personal
gentleman. In fact this Jeeves can manage more then one Wooster
(so he might not be that personal) and guide information from one
Wooster to another in an organised way making all the Woosters
march to the drones.
""")

        def lock(self):
            pass

        def unlock(self):
            pass

        def close(self):
            pass

    flow = Jeeves()
    flow.flow = {
        "": {
            "START": Drone("START", Application())
        }
    }
    flow.start()

    expected = [
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator > Jeeves.__init__((<suapp.jandw.Jeeves object at 0x000000000000>,), {})",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator < Jeeves.__init__: None",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator > Jeeves.start((<suapp.jandw.Jeeves object at 0x000000000000>,), {})",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator > Jeeves.drone((<suapp.jandw.Jeeves object at 0x000000000000>, '', 'START', 1, None), {})",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator > Jeeves.whichDrone((<suapp.jandw.Jeeves object at 0x000000000000>, '', 'START'), {})",
        "10 DEBUG suapp.jandw jandw.py jandw whichDrone : Jeeves[<suapp.jandw.Jeeves object at 0x000000000000>].whichDrone : Flow: {'': {'START': <suapp.jandw.Drone object at 0x000000000000>}}",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator < Jeeves.whichDrone: <suapp.jandw.Drone object at 0x000000000000>",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator > Drone.get_new_instance_clone((<suapp.jandw.Drone object at 0x000000000000>, None, 1), {})",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator < Drone.get_new_instance_clone: <suapp.jandw.Drone object at 0x000000000000>",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator < Jeeves.drone",
        "10 DEBUG suapp.jandw logdecorator.py logdecorator decorator < Jeeves.start: None",
    ]
    fields = ['levelno', 'levelname', 'name', 'filename', 'module', 'funcName']
    for log_line, expected in zip(handler.buffer, expected):
        line = []
        for field in fields:
            line.append(re.sub('0x[0-9a-f]*', '0x000000000000', str(getattr(log_line, field))))
        line.append(re.sub('0x[0-9a-f]*', '0x000000000000', log_line.getMessage()))
        print("E: %s\nG: %s" % (expected, " ".join(line)))
        if isinstance(expected, tuple):
            assert " ".join(line) in expected
        else:
            assert " ".join(line) == expected
