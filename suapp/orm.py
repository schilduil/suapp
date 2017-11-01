#!/usr/bin/env python3


import pony.orm
import sys


__all__ = ["UiOrmObject"]


class UiOrmObject():
    """
    Parent of all UI ORM objects.

    The PonyORM object is set as attribute _ui_orm.
    All attributes not starting with _ui_ come from the PonyORM object.
    """

    config = {}

    @staticmethod
    def uize(orm_object):
        """
        Finds the UiOrmObject from a pony.orm.core.Entity.

        It assumes the name of the UiOrmObject is the Entity name preceded
        with "Ui".
        """
        if isinstance(orm_object, pony.orm.core.Entity):
            #print("%s in %s" % (orm_object.__class__.__name__, orm_object.__class__.__module__))
            module = sys.modules[orm_object.__class__.__module__]
            ui_orm_class = getattr(module, "Ui%s" % orm_object.__class__.__name__)
            return ui_orm_class(orm=orm_object)

    def ui_init(self):
        """
        Initialize from the PonyORM object.
        """
        self.ui_attributes = set()
        for attr in self._ui_orm._attrs_:
            self.ui_attributes.add(attr.name)

    def __getattr__(self, key):
        """
        Returns all attributes.

        Normally these come directly from the PonyORM object, except those
        starting with 'ui_' or '_ui_'.
        """
        if key.startswith("_ui_") or key.startswith("ui_"):
            return super().__getattr__(key)
        else:
            return getattr(self._ui_orm, key)

    def __setattr__(self, key, value):
        """
        Sets all attributes.

        Normally these are set direclty on the PonyOrm object, except those
        starting with 'ui_' or '_ui_'.
        """
        if key.startswith("_ui_") or key.startswith("ui_"):
            super().__setattr__(key, value)
        else:
            setattr(self._ui_orm, key, value)
