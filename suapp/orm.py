#!/usr/bin/env python3


__all__ = ["UiOrmObject"]


class UiOrmObject():
    """
    Parent of all UI ORM objects.

    The PonyORM object is set as attribute _ui_orm.
    All attributes not starting with _ui_ come from the PonyORM object.
    """

    config = {}

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
        print("GETATTR %s, %s" % (self, key))
        if key.startswith("_ui_") or key.startswith("ui_"):
            print("GETATTR: super")
            return super().__getattr__(key)
        else:
            print("GETATTR: self._ui_orm")
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
