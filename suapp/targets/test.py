#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import suapp.jandw
from suapp.logdecorator import *


class Application(suapp.jandw.Wooster):

    @loguse
    def __init__(self, master=None):
        self.name = "Application"
        self.jeeves = None
        self.dataobject = None
        self.testdata = {"ID": "(150112)164", "ring": "BGC/BR23/10/164"}
        self.tables = {}

    @loguse
    def inflow(self, jeeves, drone):
        if drone.dataobject:
            self.dataobject = drone.dataobject
        if not self.dataobject:
            self.dataobject = {}
        self.name = self.dataobject.get('name', 'SuApp')
        print("=====================")
        print(self.name)
        print("---------------------")
        self.tables = self.dataobject('tables', {})
        print(self.tables)
        self.jeeves = jeeves
        print("Entered with mode %s. " % (drone.mode))
        # The about .txt should be in the same folder as the conf json.
        textfile = self.jeeves.app.configuration["self"].rsplit(".", 1)[0] + ".txt"
        print("---------------------")
        print("\tA: About")
        print("\tC: Configuration")
        print("\tX: Exit")
        answer = input("Choose option: ")
        print()
        if answer.upper() == "A":
            self.jeeves.drone(self, "ABOUT", self.jeeves.MODE_MODAL, textfile)
        elif answer.upper() == "C":
            self.jeeves.drone(self, "CONFIGURATION", self.jeeves.MODE_MODAL, textfile)
        if not answer.upper() == "X":
            self.inflow(jeeves, drone)

    @loguse
    def lock(self):
        pass

    @loguse
    def unlock(self):
        pass

    @loguse
    def close(self):
        '''
        Close as Wooster
        '''
        pass


class About(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        print("=====================")
        print("About")
        print("---------------------")
        try:
            with open("%s" % (drone.dataobject)) as fh:
                for line in fh:
                    print(line, end="")
        except OSError as e:
            logging.getLogger(self.__module__).warning("Could not open about text file %s.", drone.dataobject)
        except IOError as e:
            logging.getLogger(self.__module__).warning("Could not open about text file %s.", drone.dataobject)
        print()
        print("---------------------")
        answer = input("Choose option: ")
        print()


class Configuration(suapp.jandw.Wooster):

    @loguse
    def inflow(self, jeeves, drone):
        self.jeeves = jeeves
        import json
        print("=====================")
        print("Configuration")
        print("---------------------")
        print(json.dumps(self.jeeves.app.configuration, indent="\t"))
        print("---------------------")
        answer = input("Choose option: ")
        print()
