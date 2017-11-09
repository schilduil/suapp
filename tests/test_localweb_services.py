#!/usr/bin/env python3

import pytest


"""
 - Fetch an object by its primary key:
    http://127.0.0.1:8385/service/fetch?table=Individual&key=5&module=modlib.base&pretty
    http://127.0.0.1:8385/service/fetch?table=UiIndividual&key=5&module=modlib.base&pretty
    http://127.0.0.1:8385/service/fetch?table=Kinship&key=5&key=5&module=modlib.kinship&pretty
    http://127.0.0.1:8385/service/fetch?table=UiKinship&key=5&key=5&module=modlib.kinship&pretty

 - Run a query defined in a modlib:
    http://127.0.0.1:8385/service/query/individual.adults?pagenum=1&pagesize=5&pretty

 - Fetccj objects from a one-to-many or many-to-many link:
    http://127.0.0.1:8385/service/setfetch?table=Individual&key=5&module=modlib.base&link=first_kinships&pretty
    http://127.0.0.1:8385/service/setfetch?table=UiIndividual&key=5&module=modlib.base&link=first_kinships&pretty
"""
