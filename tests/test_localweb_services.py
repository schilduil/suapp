#!/usr/bin/env python3

#import http.client
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import pytest

sys.path.append(os.getcwd())
import suapp


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

random_string_params = [None, (0,10), (1,10), (2,20), (3,30), (4, 40), (5,1), (6,2), (7,3), (8,4), (9,5), (10,6), (11,7), (12,8), (13,9)]


def random_string(seed, length):
    random.seed(seed)
    uri = []
    for x in range(length):
        uri.append(chr(random.randint(64,122)))
    return "" # .join(uri)

@pytest.fixture(scope="module")
def launch(tmpdir_factory):
    # Launch with the localweb target, without client.
    datapath = tmpdir_factory.mktemp("data")
    logpath = tmpdir_factory.mktemp("log")
    configpath = tmpdir_factory.mktemp("config")
    flow = configpath.join("tlwt.flow")
    port = 8385
    hostname = "127.0.0.1"
    flow.write("\n".join([
        "START: Application.START",
        "ABOUT: About.IN",
        "CONFIGURATION: Configuration.IN"
    ]))
    config = {
        "datasource": {
            "type": "sqlite",
            "filename": "%s/suapp.sqlite" % (datapath)
        },
        "log": {
            "filemode": "w",
            "filename": "%s/suapp.log" % (logpath),
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "level": "DEBUG",
            "modules": {
                "httpd": {
                    "filename": "%s/httpd.accces_log" % (logpath),
                    "level": "DEBUG"
                }
            }
        },
        "httpd": {
            "client": False,
            "ip": hostname,
            "port": port,
            "background": True
        },
        "modules": {},
        "target": "localweb",
        "name": "Test LocalWeb Target",
        "shortname": "TLWT",
        "self": "%s/tlwt.yml" % (configpath)
    }
    # Let's go.
    suapp.main(config)
    time.sleep(1)
    # ServerThread is now running, so do your tests...
    print("Before")
    yield (hostname, port)
    print("After")
    # Find the ServerThread and shut it down.
    for t in threading.enumerate():
        print("Thread: %s (%r/%s) alive: %s" % (t.name, t, t, t.is_alive()))
        if t.name == "ServerThread":
            t.shutdown()

@pytest.fixture(params=random_string_params)
def random_uri(request):
    if not request.param:
        return ""
    else:
        (seed, length) = request.param
        random.seed(seed)
        uri = []
        for x in range(length):
            uri.append(chr(random.randint(64,122)))
        return "".join(uri)

@pytest.fixture
def random_service_uri(random_uri):
    return "service/" + random_uri

@pytest.fixture(params=[None, (46546,11)])
def random_random_uri(request, random_uri):
    uri = ['/']
    if request.param:
        (seed, length) = request.param
        for x in range(length):
            uri.append(chr(random.randint(64,122)))
    print("URI: %s" % (random_uri))
    print("  +: %s" % (uri))
    return random_uri + "".join(uri)

def test_random_unauthenticated(launch, random_uri):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        with urllib.request.urlopen("http://%s:%s/" % launch + random_uri) as r:
            assert True == False
    # Not logged in, so should return HTTP Error 403: Forbidden
    assert exc_info.value.getcode() == 403

def test_random_service_uri(launch, random_service_uri):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        with urllib.request.urlopen("http://%s:%s/" % launch + random_service_uri) as r:
            assert True == False
    # Not logged in, so should return HTTP Error 403: Forbidden
    assert exc_info.value.getcode() == 403

def test_random_random_uri(launch, random_random_uri):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        with urllib.request.urlopen("http://%s:%s/" % launch + random_random_uri) as r:
            assert True == False
    # Not logged in, so should return
    #   HTTP Error 403: Forbidden
    #   HTTP Error 400: Bad Request
    assert exc_info.value.getcode() in [400, 403]
