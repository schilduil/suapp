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

    def ui_definitions()
        A function returning a dictionary of UI ORM classes: subclass of
        suapp.orm.UiOrmObject that describes the UI ORM that act as interface
        between the application and the database.

    def view_definitions()
        A function returning a tuple of (queries, views, flow) where
            views is a dict of view definitions.
            queries is a dict of queries used in views.
            flow is an update on the flow.
"""

import datetime
import importlib
import logging
import sys

from pony.orm import *

import suapp.orm
from suapp.jandw import Jeeves


modules = []
db = Database()


__all__ = ["ModuleDependencyLoading", "import_modlib", "get_database", "modules"]


def get_database():
    return db


class ModuleDependencyLoading(ImportError):
    pass


def import_modlib(app_name, module_name, jeeves, scope=None, config=None):
    """
    Importing the modlib module and all dependencies.
    """
    # Listing the modules we've already loaded.
    modules_loaded = []
    if module_name in modules:
        # Already loaded, skip
        return modules_loaded
    # Initializing config and scope if not passed.
    if config is not None:
        suapp.orm.UiOrmObject.config = config
    if scope is None:
        scope = {}
    # Importing the module in Python.
    module_entity = importlib.import_module("modlib.%s" % (module_name))
    # Checking if the app matches in the module.
    if app_name:
        if app_name != module_entity.app_name:
            # Wrong app type: skipping and warn about it.
            logging.getLogger(__name__).warning(
                "Skipping module %s (%s) as it does not belong to app %s.",
                module_name,
                module_entity.app_name,
                app_name,
            )
            return False
    else:
        # Initializing it if it isn't set yet.
        app_name = module_entity.app_name
    # First making sure all requirement modules are loaded.
    for requirement_name in module_entity.requirements():
        # Checking if we've already done the required module.
        if requirement_name not in modules:
            # Trying to import
            required_modules_loaded = import_modlib(
                app_name, requirement_name, jeeves, scope
            )
            if not required_modules_loaded:
                # Import of the requirement failed.
                raise ModuleDependencyLoading(
                    "Could not load datamodule %s because requirement %s failed to load."
                    % (module_name, requirement_name)
                )
            modules_loaded.extend(required_modules_loaded)
    # Loading all the PonyORM classes into the global scope.
    classes_dict = module_entity.definitions(db, scope)
    if "modlib" not in globals():
        scope["modlib"] = sys.modules["modlib"]
        globals().update({"modlib": sys.modules["modlib"]})
    for name, value in classes_dict.items():
        setattr(sys.modules[value.__module__], name, value)
    scope["suapp"] = sys.modules["suapp"]
    # Loading all the UI ORM classes in to the global scope.
    classes_dict = module_entity.ui_definitions(db, scope)
    for name, value in classes_dict.items():
        setattr(sys.modules[value.__module__], name, value)
    # Loading the views.
    (queries, views, flow) = module_entity.view_definitions()
    if queries:
        jeeves.queries.update(queries)
    if flow:
        jeeves.flow.update(flow)
    if views:
        jeeves.views.update(views)
    # Adding to the list of imported modules.
    modules.append(module_name)
    modules_loaded.append(module_name)
    logging.getLogger(__name__).info("Loaded %s.", module_name)
    return modules_loaded


if __name__ == "__main__":

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
        modules_to_import = ["base"]

    scope = {}
    for mod in modules_to_import:
        import_modlib(app_name, mod, Jeeves(), scope)

    print("Modules: %s" % (modules))

    db.bind("sqlite", ":memory:")
    db.generate_mapping(create_tables=True)

    with db_session():
        try:
            # === BASE === "
            print(modlib.base.Individual.mro())
            vayf = modlib.base.Individual(
                code="VAYF", dob=datetime.date(year=2007, month=1, day=1)
            )
            goc = modlib.base.Individual(
                code="GOc", dob=datetime.date(year=2006, month=1, day=1)
            )
            govayf62 = modlib.base.Individual(
                code="(GOVAYF)62",
                dob=datetime.datetime(year=2008, month=1, day=1),
                parents=[goc, vayf],
            )
            ac = modlib.base.Individual(
                code="AC", dob=datetime.datetime(year=2009, month=1, day=1)
            )
            ac62110 = modlib.base.Individual(
                code="(AC62)110",
                dob=datetime.datetime(year=2010, month=1, day=1),
                parents=[ac, govayf62],
            )
            ac110280 = modlib.base.Individual(
                code="(AC110)280",
                dob=datetime.datetime(year=2011, month=1, day=1),
                parents=[ac, ac62110],
            )
            print(vayf)
            print(goc)
            print(modlib.kinship.Kinship.mro())
            print(goc._attrs_)

            # === KINSHIP === #
            k_goc_vayf = modlib.kinship.Kinship(first=goc, second=vayf, kinship=0.0)
            ui_k_goc_vayf = modlib.kinship.UiKinship(orm=k_goc_vayf)
            print(
                "%s, %s: %s"
                % (
                    ui_k_goc_vayf.first.code,
                    ui_k_goc_vayf.second.code,
                    ui_k_goc_vayf.kinship,
                )
            )
            flush()
            ui_k_goc_vayf = modlib.kinship.UiKinship(first=vayf, second=goc)
            print(
                "%s, %s: %s"
                % (
                    ui_k_goc_vayf.first.code,
                    ui_k_goc_vayf.second.code,
                    ui_k_goc_vayf.kinship,
                )
            )

            print("Parents (GOVAYF)62: %s" % (govayf62.parents.page(1, pagesize=2)))
            print("")

            # Start calculation inbreeding
            i = modlib.base.UiIndividual(orm=ac110280)
            print("Record: %s" % (i._ui_orm))
            for key in sorted(i.ui_attributes):
                print("\t%s: %s" % (key, getattr(i, key)))
            print("")
            print("Record: %s" % (i._ui_orm))
            for key in sorted(i.__dict__):
                print("\t%s: %s" % (key, getattr(i, key)))
            print("")

            print("Record: %s" % (ui_k_goc_vayf))
            for key in sorted(ui_k_goc_vayf.ui_attributes):
                print("\t%s: %s" % (key, getattr(ui_k_goc_vayf, key)))
            print("")

            print("Calculated kinships:")
            for kinship in select(c for c in modlib.kinship.Kinship):
                if kinship.pc_kinship:
                    print(
                        "\t%s, %s: %2.2f%% (%2.2f%%)"
                        % (
                            kinship.first.code,
                            kinship.second.code,
                            kinship.kinship * 100.00,
                            kinship.pc_kinship * 100.00,
                        )
                    )
                else:
                    print(
                        "\t%s, %s: %2.2f%%"
                        % (
                            kinship.first.code,
                            kinship.second.code,
                            kinship.kinship * 100.00,
                        )
                    )
            print("")
            print(
                "Inbreeding in %s is: %2.2f%% (%2.2f%%)"
                % (i.code, (i.ui_inbreeding) * 100.00, (i.ui_pc_inbreeding) * 100.00)
            )
            print("")
        except:
            # raise
            pass
