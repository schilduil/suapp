#!/usr/bin/env python3

import pytest

import copy
import json
import os
import os.path
import pprint
import tempfile
import sys
import urllib.error

sys.path.append(os.path.join(os.getcwd(), 'suapp'))
import orm

def test_orm():
    class Test(orm.UiOrmObject):
        pass
    test = Test()
