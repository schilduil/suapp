#!/usr/bin/env python3

import pytest

import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'suapp/targets/localweb'))
import simple_json


class Something():

    def __init__(self, name):
        self.name = name

    def toJSON(self):
        return {"name": self.name}


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


def test_dict_with_objects():
    assert simple_json.dumps(x, sort_keys=True) == json.dumps(x_analog, sort_keys=True)

def test_dict_with_objects_indented():
    assert simple_json.dumps(x, indent=4, sort_keys=True) == json.dumps(x_analog, indent=4, sort_keys=True)
