#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Loads to datamodels of modules.

A module must have a datamodel.py for this to work:
    modlib/<module>/datamodel.py

The datamodel.py must have the following elements:
    app_name
        A string with the name of the app to which this module belongs.

    def requirements()
        A function returning a list of modules required by this module.

    def definitions()
        A function returning a dictionary of names: subclass of db.Entity
        that describe the database tables of the module.
"""

import importlib
import logging
import sys

from pony.orm import *


modules = []
db = Database()


class ModuleException(Exception):
    pass


class ModuleLoadingException(ModuleException):
    pass


def import_modlib(app_name, module_name, scope):
    """
    Importing the modlib module and al dependencies.
    """
    # Importing the module in Python.
    module_entity = importlib.import_module("modlib.%s" % (module_name))
    # Checking if the app matches in the module.
    if app_name:
        if app_name != module_entity.app_name:
            # Wrong app type: skipping and warn about it.
            logging.getLogger(__name__).warn("Skipping module %s (%s) as it does not belong to app %s." % (module_name, module_entity.app_name, app_name))
            return False
    else:
        # Initializing it if it isn't set yet.
        app_name = module_entitiy.app_name
    # First making sure all requirement modules are loaded.
    for requirement_name in module_entity.requirements():
        # Checking if we've already done the required module.
        if requirement_name not in modules:
            # Trying to import
            if not import_modlib(app_name, requirement_name, scope):
                # Import of the requirement failed.
                raise ModuleLoadingException("Could not load datamodule %s because requirement %s failed to load." % (module_name, requirement_name))
    # Loading all the PonyORM classes into the global scope.
    classes_dict = module_entity.definitions(db, scope)
    if 'modlib' not in globals():
        scope['modlib'] = sys.modules['modlib']
        globals().update({'modlib': sys.modules['modlib']})
    for name, value in classes_dict.items():
        setattr(sys.modules[value.__module__], name, value)
    # Adding to the list of imported modules.
    modules.append(module_name)
    logging.getLogger(__name__).info("Loaded %s." % (module_name))
    return True


if __name__ == '__main__':

    # Default settings
    app_name = "suapp"
    modules_to_import = []

    # Parsing command line arguments.
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
    if len(sys.argv) > 2:
        for mod in sys.argv[2:]:
            modules_to_import.append(mod)

    # If no modules, at least do base.
    if not modules_to_import:
        modules_to_import = ['base']

    scope = {}
    for mod in modules_to_import:
        import_modlib(app_name, mod, scope)

    print("Modules: %s" % (modules))

    db.bind("sqlite", ":memory:")
    db.generate_mapping(create_tables=True)

    with db_session():
        try:
            print(modlib.base.Individual.mro())
            vayf = modlib.base.Individual(code="VAYF")
            goc = modlib.base.Individual(code="GOc")
            print(vayf)
            print(goc)
            print(modlib.kinship.Kinship.mro())
            k_goc_vayf = modlib.kinship.Kinship(first=goc, second=vayf, kinship=0.0)
            print(k_goc_vayf)
        except:
            pass
