#!/usr/bin/env python3

import pytest

import copy
import json
import os
import os.path
import pony.orm
import pprint
import tempfile
import sys
import urllib.error

sys.path.append(os.getcwd())
import suapp.orm

@pytest.fixture(params=[None, "five"])
def pony_entity(request):
    db = pony.orm.Database()
    class TestOrm(db.Entity):
        one = pony.orm.Optional(int)
        two = pony.orm.Optional(int)
        three = pony.orm.Optional(int)
        four = pony.orm.Optional(int)
    if request.param == "five":
        class SubTestOrm(TestOrm):
            five = pony.orm.Optional(int)
        return (db, SubTestOrm)
    else:
        return (db, TestOrm)

@pytest.fixture()
def pony_entity_object(pony_entity):
    (db, TestOrm) = pony_entity
    db.bind("sqlite", ":memory:")
    db.generate_mapping(create_tables=True)
    with pony.orm.db_session():
        orm_object = TestOrm(one=1,two=2,three=3,four=4)
        yield orm_object

@pytest.fixture()
def orm_objects(pony_entity_object):
    class UiTestOrm(suapp.orm.UiOrmObject):
        def __init__(self, orm=None):
            pass
    class UiSubTestOrm(UiTestOrm):
        pass
    test = UiTestOrm()
    test._ui_orm = pony_entity_object
    test.ui_init()
    setattr(sys.modules[pony_entity_object.__class__.__module__], "UiTestOrm", UiTestOrm)
    setattr(sys.modules[pony_entity_object.__class__.__module__], "UiSubTestOrm", UiSubTestOrm)
    return (pony_entity_object, test)

def test_orm(orm_objects):
    (pony_entity_object, ui_orm_object) = orm_objects
    assert ui_orm_object.one is pony_entity_object.one
    assert ui_orm_object.two is pony_entity_object.two
    assert ui_orm_object.three is pony_entity_object.three
    assert ui_orm_object.four is pony_entity_object.four

def test_ui_orm(orm_objects):
    (pony_entity_object, ui_orm_object) = orm_objects
    assert ui_orm_object._ui_orm is pony_entity_object

def test_columns(orm_objects):
    (pony_entity_object, ui_orm_object) = orm_objects
    assert pony_entity_object._pk_columns_ == ["id"]
    assert ui_orm_object._pk_columns_ == ["id"]

def test_uize(orm_objects):
    (pony_entity_object, ui_orm_object) = orm_objects
    assert suapp.orm.UiOrmObject.uize(pony_entity_object).__class__.__name__ == "Ui%s" % (pony_entity_object.__class__.__name__)

def test_ui_attributes(orm_objects):
    (pony_entity_object, ui_orm_object) = orm_objects
    x = "This is me."
    ui_orm_object._ui_x = x
    assert ui_orm_object._ui_x is x
