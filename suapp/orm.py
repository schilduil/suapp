class UiOrmObject():
    """
    Parent of all UI ORM objects.

    The PonyORM object is set as attribute _ui_orm.
    All attributes not starting with _ui_ come from the PonyORM object.
    """
    def __init__(self, orm):
        """
        Initialize with PonyORM object in orm
        """
        self._ui_orm = orm

    def __getattr__(self, key):
        """
        Returns all attributes.

        Normally these come directly from the PonyORM object, except those
        starting with 'ui_' or '_ui_'.
        """
        if key.startswith("_ui_") or key.startswith("ui_"):
            print("Super: %s" % (super()))
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
