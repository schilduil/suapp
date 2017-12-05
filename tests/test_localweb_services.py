#!/usr/bin/env python3

import os
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

# scope="module"
@pytest.fixture()
def launch(tmpdir):
    # Launch with the localweb target, without client.
    datapath = tmpdir.mkdir("data")
    logpath = tmpdir.mkdir("log")
    configpath = tmpdir.mkdir("config")
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
    yield (hostname, port)
    # Find the ServerThread and shut it down.
    for t in threading.enumerate():
        # print("Thread: %s (%r/%s) alive: %s" % (t.name, t, t, t.is_alive()))
        if t.name == "ServerThread":
            t.shutdown()

@pytest.fixture(params=[None])
def random_uri(request):
    if not request.param:
        return ""


def test_unauthenticated(launch, random_uri):
    print(launch)
    print(dir(suapp.targets.localweb))
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        with urllib.request.urlopen("http://%s:%s/" % launch + random_uri) as r:
            assert True == False
    # Not logged in, so should return HTTP Error 403: Forbidden
    assert exc_info.value.getcode() == 403
