class UiOrmObject():
    def __init__(self, orm):
        self._ui_orm = orm

    def __getattr__(self, key):
        if key.startswith("_ui_"):
            return super().__getattr__(key)
        else:
            return getattr(self._ui_orm, key)

    def __setattr__(self, key, value):
        if key.startswith("_ui_"):
            super().__setattr__(key, value)
        else:
            # to_field
            setattr(self._ui_orm, key, value)
