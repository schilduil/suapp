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
import configuration


# Sample configuration we're expecting.
sample = {
    "name": "SU Demo Application",
    "shortname": "suapp",
    "log": {
        "filename": "~/.suapp/log/suapp.log",
        "filemode": "w",
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        "level": "INFO",
        "modules": {
            "base": {
                "level": "INFO"
            },
            "httpd": {
                "level": "DEBUG",
                "filename": "~/.suapp/log/httpd.accces_log"
            }
        }
    },
    "datasource": {
        "type": "Plank",
        "location": "~/.susm/data/"
    },
    "modules": {
        "base": {}
    }
}

difference = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "modules": {
        "base": {},
        "location": {},
    }
}

different_sample = copy.deepcopy(sample)
different_sample.update(difference)

# URL used for tests.
url = 'https://raw.githubusercontent.com/schilduil/suapp/master/suapp.json'

def lowest_level(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            continue
        result[key] = value
    return result

def add_extra_everywhere(source, extra):
    result = {}
    for key, value in source.items():
        if isinstance(value, dict):
            result[key] = add_extra_everywhere(value, extra)
            result[key].update(extra)
        else:
            result[key] = value
    return result

def file_name(suffix):
    """ Test fixture to a temporary file name. """
    (os_level_handle, file_name) = tempfile.mkstemp(suffix=suffix)
    os.close(os_level_handle)
    os.remove(file_name)
    return file_name

@pytest.fixture
def json_file():
    """ Test fixture to a temporary json file name. """
    name = file_name('.json')
    yield name
    # Cleaning up after itself.
    try:
        os.remove(name)
    except:
        pass

@pytest.fixture
def cfg_file():
    """ Test fixture to a temporary json file name. """
    name = file_name('.cfg')
    yield name
    # Cleaning up after itself.
    try:
        os.remove(name)
    except:
        pass

def test_dictionary():
    """ Test initializing the configuration with a dictionary. """
    with configuration.get_configuration(copy.deepcopy(sample)) as test:
        assert test == sample

@pytest.mark.xfail(raises=urllib.error.URLError)
def test_url():
    """
    Test getting the configuration from a url.

    This depends on the network and the url being available. So a URLError
    should not mean a failure, just an xfail.
    """
    with configuration.get_configuration(url) as test:
        assert test == sample

@pytest.mark.xfail(raises=[urllib.error.URLError,NotImplementedError])
def test_missing_json_with_backup(json_file):
    """
    Test with a json file (that does not exists) with backup.

    Should fall back to the url (or dictionary).
    This depends on the network and the url being available. So a URLError
    should not mean a failure, just an xfail.
    Similarly it will try to save on exit, raising a NotImplementedError
    as that is not implemented for a WebConfiguration. So that as well should
    not be seen as a failure, just an xfail.
    """
    with configuration.get_configuration([json_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample
        assert json.load(open(json_file)) == sample

def test_new_empty_json_file_with_add_and_save(json_file):
    """ Test an empty json file configuration with modification via add. """
    expected = {'c': 'python'}
    with configuration.get_configuration([json_file, {}]) as test:
        for key in expected:
            test[key] = copy.deepcopy(expected[key])
        test.save()
    print("File: %s" % (json_file))
    print("=== START FILE CONTENT ===")
    for line in open(json_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===")
    with configuration.get_configuration(json_file) as test:
        assert test == expected

def test_new_empty_json_file_with_update_and_save(json_file):
    """ Test an empty json file configuration with modification via update. """
    expected = {'c': 'python'}
    with configuration.get_configuration([json_file, {}]) as test:
        test.update(expected)
        test.save()
    print("File: %s" % (json_file))
    print("=== START FILE CONTENT ===")
    for line in open(json_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===")
    with configuration.get_configuration(json_file) as test:
        assert test == expected

def test_different_json_file_with_backup(json_file):
    """ Test a different json file than the backups. """
    print("Configuration: %s" % (different_sample))
    fp = open(json_file, 'w')
    json.dump(different_sample, fp)
    fp.close()
    print("File: %s" % (json_file))
    print("=== START FILE CONTENT ===")
    for line in open(json_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===")
    with configuration.get_configuration([json_file, url, copy.deepcopy(sample)]) as test:
        assert test == different_sample

def test_missing_cfg_file_with_backup(cfg_file):
    """ Test with a cfg file that doesn't exist yet and backup. """
    with configuration.get_configuration([cfg_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample

    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")

def test_different_cfg_with_backup(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with configuration.get_configuration([cfg_file, different_sample]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    # TODO: Need to make a similar test but with extra option sparse=False
    # TODO: Need to make a similar test but with extra option raw=False
    with configuration.get_configuration([cfg_file, url, sample], raw=True) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Different sample:")
        pprint.pprint(different_sample)
        assert test == different_sample

def notest_different_cfg_with_backup_not_sparse(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with configuration.get_configuration([cfg_file, different_sample]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    expected = add_extra_everywhere(different_sample, lowest_level(different_sample))
    with configuration.get_configuration([cfg_file, url, sample], sparse=False) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Expected based on different sample:")
        pprint.pprint(expected)
        assert test == expected

def notest_different_cfg_with_backup_not_raw(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with configuration.get_configuration([cfg_file, different_sample]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    with configuration.get_configuration([cfg_file, url, sample], raw=False) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Different sample:")
        pprint.pprint(different_sample)
        assert test == different_sample

"""
# TEST 9: xml
# Creating a temporary file for the configuration.
    (os_level_handle, file_name) = tempfile.mkstemp(suffix=".xml")
    os.close(os_level_handle)
    os.remove(file_name)
    print("TEST 9: passing a xml file and a backup URL where the file doesn't exist: %s, %s" % (file_name, url))
    print("\tDoes the file exists (should be False): %s." % (os.path.isfile(file_name)))
    with get_configuration([file_name, url, sample]) as test:
        print("\t%s\n" % (test))

    print("=== START FILE CONTENT ===")
    for line in open(file_name, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")

# TEST 10: xml file/url/sample (file exists)
    print("TEST 10: passing a xml file and a backup URL where the file exists: %s, %s" % (file_name, url))
    print("\tDoes the file exists (should be True): %s." % (os.path.isfile(file_name)))
    with get_configuration([file_name, url, sample]) as test:
        print("\t%s\n" % (test))

    print("=== START FILE CONTENT ===")
    for line in open(file_name, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")

    os.remove(file_name)

# TEST 11: yaml
# Creating a temporary file for the configuration.
    (os_level_handle, file_name) = tempfile.mkstemp(suffix=".yaml")
    os.close(os_level_handle)
    os.remove(file_name)
    print("TEST 11: passing a yaml file and a backup URL where the file doesn't exist: %s, %s" % (file_name, url))
    print("\tDoes the file exists (should be False): %s." % (os.path.isfile(file_name)))
    with get_configuration([file_name, url, sample]) as test:
        print("\t%s\n" % (test))

    print("=== START FILE CONTENT ===")
    for line in open(file_name, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")

# TEST 12: xml file/url/sample (file exists)
    print("TEST 12: passing a yaml file and a backup URL where the file exists: %s, %s" % (file_name, url))
    print("\tDoes the file exists (should be True): %s." % (os.path.isfile(file_name)))
    with get_configuration([file_name, url, sample]) as test:
        print("\t%s\n" % (test))

    print("=== START FILE CONTENT ===")
    for line in open(file_name, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")

    os.remove(file_name)
"""
