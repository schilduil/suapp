#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Copyright (C), 2013, The Schilduil Team. All rights reserved.
"""
import sys

from suapp.logdecorator import *


class Wooster(object):
    """
    A Wooster represents a UI window/page.

    GENERALLY THESE THINGS ARE REUSED SO YOU NEED TO BE VERY CAREFUL ABOUT SIDE EFFECTS.
    In case you have something that cannot be reused do something like:
        1/ Create a new class instance of a subclass of Wooster
        2/ Call inflow on that
    """
    def lock(self):
        pass

    def unlock(self):
        pass

    def inflow(self, jeeves, drone):
        # The only thing it does is store the Jeeves object.
        self.jeeves = jeeves
        # MODE: Modal=1, Replace=2, Both=3
        # jeeves.drone(self, name, mode, dataobject)

    def close(self):
        pass


class Drone(object):
    """
    A drone is the connection between two vertices.
    """
    def __init__(self, name, tovertex):
        self.name = name
        self.tovertex = tovertex


class Jeeves(object):
    """
    Jeeves is the controller that determins the flow.

    It uses Drones to go from Wooster to Wooster.
    """
    MODE_OPEN = 3
    MODE_REPLACE = 2
    MODE_MODAL = 1

    @loguse
    def __init__(self, app=None):
        """
        Initializes the Jeeves with an empty flow and app name.
        """
        self.flow = {"": {}}
        self.app = app
        self.views = {}
        self.queries = {}
        self.ormscope = {}

    @loguse
    def whichDrone(self, fromname, outmessage, **kwargs):
        """
        Finding the drone matching the outmessage.
        """
        logging.getLogger(__name__).debug(": Jeeves[%r].whichDrone : Flow: %s" % (self, self.flow))
        drone = None
        try:
            drone = self.flow[fromname][outmessage]
        except:
            try:
                drone = self.flow[""][outmessage]
            except:
                # TODO: do something else then bluntly exiting.
                logging.getLogger(__name__).error(": Jeeves[%r].whichDrone : Not found '%s' - exiting." % (self, outmessage))
                if outmessage is "OUT":
                    sys.exit(0)
                else:
                    sys.exit(100)
        return drone

    @loguse('@')  # Not logging the return value.
    def do_query(self, name, scope=None, params=None):
       """
       Execute a query by name and return the result.
       """
       if scope is None:
           scope = {}
       query_template, defaults = self.queries[name]
       parameters = defaults.copy()
       parameters.update(params)
       query = query_template % parameters
       exec("result = %s" % (query), scope)
       return scope['result']

    @loguse('@')  # Not logging the return value.
    def drone(self, fromvertex, name, mode, dataobject, **kwargs):
        """
        Find the drone and execute it.
        """
        # Find the drone
        fromname = ""
        result = None
        if isinstance(fromvertex, Wooster):
            fromname = fromvertex.name
        else:
            fromname = str(fromvertex)
        drone = self.whichDrone(fromname, name, **kwargs)
        # Setting the dataobject
        drone.dataobject = dataobject
        drone.mode = mode
        # If there is a callback, call it.
        if 'callback_drone' in kwargs:
            try:
                kwargs['callback_drone'](drone)
            except:
                pass
        # Depending on the mode
        # Some targets depend on what is returned from inflow.
        if mode == self.MODE_MODAL:
            if isinstance(fromvertex, Wooster):
                fromvertex.lock()
                drone.fromvertex = fromvertex
            result = drone.tovertex.inflow(self, drone)
            if isinstance(fromvertex, Wooster):
                fromvertex.unlock()
        elif mode == self.MODE_REPLACE:
            drone.fromvertex = None
            fromvertex.close()
            result = drone.tovertex.inflow(self, drone)
        elif mode == self.MODE_OPEN:
            drone.fromvertex = fromvertex
            result = drone.tovertex.inflow(self, drone)
        return result

    @loguse
    def start(self, dataobject=None):
        """
        Start the Jeeves flow.
        """
        self.drone("", "START", self.MODE_MODAL, dataobject)


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level=logging.DEBUG)
    logging.getLogger("__main__").setLevel(logging.DEBUG)
    modulename = "__main__"
    print("__main__: %s (%s)" % (modulename, logging.getLevelName(logging.getLogger(modulename).getEffectiveLevel())))

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
