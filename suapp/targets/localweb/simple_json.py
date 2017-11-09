#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
from pony.orm.core import Entity, SetInstance, Required, Optional

import suapp.orm


__all__ = ["to_json", "dumps"]


def to_json(object_to_serialize):
    """
    Adding simple serialization for objects.

    If standard json.dumps fails and it is a real object it will try to call
    toJSON() on it. If that fails it will return a TypeError.
    """
    result = {}
    if isinstance(object_to_serialize, Entity):
        for attr in object_to_serialize._attrs_:
            column = attr.name
            result[column] = getattr(object_to_serialize, column)
    elif isinstance(object_to_serialize, suapp.orm.UiOrmObject):
        for column in object_to_serialize.ui_attributes:
            result[column] = getattr(object_to_serialize, column)
    else:
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
        return result
    # Also putting out the primary key
    result['_pk_'] = object_to_serialize._pk_
    #result['__str__'] = "%s" % (object_to_serialize)
    # Checking for foreign keys
    for column, value in result.items():
        if isinstance(value, Entity):
            value = value._pk_
            # Setting it
            # If is a Set or tuple it will be set again below.
            result[column] = value
        if isinstance(value, SetInstance):
            # An empty dictonary signals a Set.
            result[column] = {}
        elif isinstance(value, tuple):
            # On json a tuple = list, so might as well use a list.
            converted_tuple = []
            for subvalue in value:
                # Finding out the references to variables.
                if isinstance(subvalue, Required) or isinstance(subvalue, Optional):
                    cur_obj = object_to_serialize
                    path = str(subvalue).split(".")[1:]
                    while len(path) > 0:
                        subvalue = getattr(cur_obj, path.pop(0))
                        cur_obj = subvalue
                if isinstance(subvalue, Entity):
                    subvalue = subvalue._pk_
                converted_tuple.append(subvalue)
            result[column] = converted_tuple
    return result

def dumps(object_to_serialize, **kwargs):
    kwargs['default'] = to_json
    return json.dumps(object_to_serialize, **kwargs)
