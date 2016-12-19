class UiOrmClass():
    def __init__(self, orm):
        self.orm = orm

    def __getattr__(self, key):
        if key == 'orm':
            return super().__getattr__(key)
        else:
            # to_visual
            return getattr(self.orm, key)

    def __setattr__(self, key, value):
        if key == 'orm':
            super().__setattr__(key, value)
        else:
            # to_field
            setattr(self.orm, key, value)
