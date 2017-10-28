#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json


def to_json(object_to_serialize):
    """
    Adding simple serialization for objects.

    If standard json.dumps fails and it is a real object it will try to call
    toJSON() on it. If that fails it will return a TypeError.
    """
    try:
        return json.dumps(object_to_serialize)
    except TypeError as te:
        if isinstance(object_to_serialize, object):
            try:
                return getattr(object_to_serialize, "toJSON")()
            except AttributeError:
                raise TypeError(repr(object_to_serialize) + " is not JSON serializable")
        # Re-raising the TypeError
        raise


def dumps(object_to_serialize, **kwargs):
    kwargs['default'] = to_json
    return json.dumps(object_to_serialize, **kwargs)


if __name__ == "__main__":

    class Something():

        def __init__(self, name):
            self.name = name

        def toJSON(self):
            return {"name": self.name}

    class OtherThing():
        def toJSON(self):
            return "OtherThing %s" % (hex(self.__hash__()))

    x = {
        0: Something("zero"),
        1: Something("one"),
        2: Something("two")
    }

    print(dumps(x, indent=4))
    print(dumps(OtherThing(), indent=4))