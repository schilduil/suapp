#!/usr/bin/env python3

import pytest

import json
import os
import sys

sys.path.append(os.getcwd())
import suapp.orm
import suapp.simple_json as simple_json


class Attribute():
    def __init__(self, name):
        self.name = name


class UnSerializableSomething():
    pass


class Something():

    def __init__(self, name):
        self.name = name
        self._attrs_ = [Attribute("name")]
        self._columns_ = ["name"]
        self._pk_ = self.name

    def toJSON(self):
        return {"name": self.name}


class OrmSomething(suapp.orm.UiOrmObject):

    def __init__(self, name):
        self._ui_orm = Something(name)
        self.ui_init()


x = {
        0: Something("zero"),
        1: Something("one"),
        2: Something("two")
}

x_analog = {
        0: {'name': 'zero'},
        1: {'name': 'one'},
        2: {'name': 'two'}
}

x_orm = {
        0: OrmSomething("zero"),
        1: OrmSomething("one"),
        2: OrmSomething("two")
}

x_orm_analog = {
        0: {'_pk_': 'zero', 'name': 'zero'},
        1: {'_pk_': 'one', 'name': 'one'},
        2: {'_pk_': 'two', 'name': 'two'}
}



def test_dict_with_objects():
    assert simple_json.dumps(x, sort_keys=True) == json.dumps(x_analog, sort_keys=True)

def test_dict_with_objects_indented():
    assert simple_json.dumps(x, indent=4, sort_keys=True) == json.dumps(x_analog, indent=4, sort_keys=True)

def test_dict_with_orm_objects():
    assert simple_json.dumps(x_orm, sort_keys=True) == json.dumps(x_orm_analog, sort_keys=True)

def test_dict_with_orm_objects_indented():
    assert simple_json.dumps(x_orm, indent=4, sort_keys=True) == json.dumps(x_orm_analog, indent=4, sort_keys=True)

def test_no_serializable():
    with pytest.raises(TypeError):
        simple_json.dumps(UnSerializableSomething())
