#!/usr/bin/env python3

import pytest

import copy
import json
import os
import os.path
import pprint
import re
import tempfile
import sys
import urllib.error

sys.path.append(os.getcwd())
import suapp.configuration


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

def recursively_unorder(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            value = recursively_unorder(value)
        result[key] = value
    return result

def lowest_level(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            continue
        result[key] = value
    return result

def add_extra_everywhere(source, extra):
    result = {}
    has_a_value = False
    has_a_dict = False
    for key, value in source.items():
        if isinstance(value, dict):
            has_a_dict = True
            result[key] = add_extra_everywhere(value, extra)
        else:
            has_a_value = True
            result[key] = value
    # If this is not only a dict of dicts.
    if has_a_value or not has_a_dict:
        result.update(extra)
    return result

def unsparse(d):
    return add_extra_everywhere(d, lowest_level(d))

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

@pytest.fixture(params=('cfg', 'ini'))
def cfg_file(request):
    """ Test fixture to a temporary configuration file name. """
    name = file_name('.%s' % (request.param))
    yield name
    # Cleaning up after itself.
    try:
        os.remove(name)
    except:
        pass

@pytest.fixture
def xml_file():
    """ Test fixture to a temporary xml file name. """
    name = file_name('.xml')
    yield name
    # Cleaning up after itself.
    try:
        os.remove(name)
    except:
        pass

@pytest.fixture(params=('yaml', 'yml'))
def yaml_file(request):
    """ Test fixture to a temporary yaml file name. """
    name = file_name('.%s' % (request.param))
    yield name
    # Cleaning up after itself.
    try:
        os.remove(name)
    except:
        pass

def test_dictionary():
    """ Test initializing the configuration with a dictionary. """
    with suapp.configuration.get_configuration(copy.deepcopy(sample)) as test:
        assert test == sample

@pytest.mark.xfail(raises=urllib.error.URLError)
def test_url():
    """
    Test getting the configuration from a url.

    This depends on the network and the url being available. So a URLError
    should not mean a failure, just an xfail.
    """
    with suapp.configuration.get_configuration(url) as test:
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
    with suapp.configuration.get_configuration([json_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample
        assert json.load(open(json_file)) == sample

def test_empty_json_file_with_add_and_save(json_file):
    """ Test an empty json file configuration with modification via add. """
    expected = {'c': 'python'}
    with suapp.configuration.get_configuration([json_file, {}]) as test:
        for key in expected:
            test[key] = copy.deepcopy(expected[key])
        test.save()
    print("File: %s" % (json_file))
    print("=== START FILE CONTENT ===")
    for line in open(json_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===")
    with suapp.configuration.get_configuration(json_file) as test:
        assert test == expected

def test_empty_json_file_with_update_and_save(json_file):
    """ Test an empty json file configuration with modification via update. """
    expected = {'c': 'python'}
    with suapp.configuration.get_configuration([json_file, {}]) as test:
        test.update(expected)
        test.save()
    print("File: %s" % (json_file))
    print("=== START FILE CONTENT ===")
    for line in open(json_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===")
    with suapp.configuration.get_configuration(json_file) as test:
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
    with suapp.configuration.get_configuration(json_file) as test:
        assert test == different_sample

def test_missing_cfg_file_with_backup(cfg_file):
    """ Test with a cfg file that doesn't exist yet and backup. """
    with suapp.configuration.get_configuration([cfg_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample

def test_different_cfg_with_backup(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with suapp.configuration.get_configuration([cfg_file, copy.deepcopy(different_sample)]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    with suapp.configuration.get_configuration(cfg_file, raw=True) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Different sample:")
        pprint.pprint(different_sample)
        assert test == different_sample

def test_different_cfg_with_backup_not_sparse(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with suapp.configuration.get_configuration([cfg_file, copy.deepcopy(different_sample)]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    expected = unsparse(different_sample)
    with suapp.configuration.get_configuration(cfg_file, sparse=False) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Expected based on different sample:")
        pprint.pprint(expected)
        assert test == expected

def notest_different_cfg_with_backup_not_raw(cfg_file):
    """ Test with a different cfg file than the backups. """
    # Creating the cfg with a different sample configuration.
    with suapp.configuration.get_configuration([cfg_file, copy.deepcopy(different_sample)]) as test:
        test.save()
    print("File: %s" % (cfg_file))
    print("=== START FILE CONTENT ===")
    for line in open(cfg_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    with suapp.configuration.get_configuration(cfg_file, raw=False) as test:
        print("Test:")
        pprint.pprint(dict(test))
        print("Different sample:")
        pprint.pprint(different_sample)
        assert test == different_sample

def test_missing_xml_with_backup(xml_file):
    """ Test with a missing xml with backup. """
    with suapp.configuration.get_configuration([xml_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample

def test_different_xml_with_backup(xml_file):
    """ Test with an existing xml with different backup """
    with suapp.configuration.get_configuration([xml_file, copy.deepcopy(different_sample)]) as test:
        test.save()
    print("File: %s" % (xml_file))
    print("=== START FILE CONTENT ===")
    for line in open(xml_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    with suapp.configuration.get_configuration(xml_file) as test:
        assert recursively_unorder(test) == different_sample

def test_missing_yaml_with_backup(yaml_file):
    """ Test with a missing yaml with backup. """
    with suapp.configuration.get_configuration([yaml_file, url, copy.deepcopy(sample)]) as test:
        assert test == sample

def test_different_yaml_with_backup(yaml_file):
    """ Test with a different yaml with backup. """
    with suapp.configuration.get_configuration([yaml_file, copy.deepcopy(different_sample)]) as test:
        test.save()
    print("=== START FILE CONTENT ===")
    for line in open(yaml_file, 'r', encoding='utf-8'):
        print(line.rstrip())
    print("=== END FILE CONTENT ===\n")
    with suapp.configuration.get_configuration(yaml_file) as test:
        assert test == different_sample

def test_ConfigurationParser():
    """
    Test the string representation.
    """
    conf = suapp.configuration.ConfigurationParser("here")
    string = re.sub('0x[0-9a-f]*', '0x000000000000', "%s" % (conf))
    assert string == "<suapp.configuration.ConfigurationParser object at 0x000000000000> on location here"

def test_load_into_dict():
    """
    Test the not supported of load_into_dict.
    """
    with pytest.raises(NotImplementedError):
        conf = suapp.configuration.ConfigurationParser("here")
        conf.load_into_dict(conf)

def test_save_from_dict():
    """
    Test the not supported of save_from_dict.
    """
    with pytest.raises(NotImplementedError):
        conf = suapp.configuration.ConfigurationParser("here")
        conf.save_from_dict(conf)

@pytest.fixture
def empty_subclass_ConfigurationParser():
    """
    Returns and empty subclass of ConfigurationParser.
    """
    class SubConfigurationParser(suapp.configuration.ConfigurationParser):
        pass
    return SubConfigurationParser

def test_sub_ConfigurationParser(empty_subclass_ConfigurationParser):
    """
    Test the string representation.
    """
    conf = empty_subclass_ConfigurationParser("here")
    string = re.sub('0x[0-9a-f]*', '0x000000000000', "%s" % (conf))
    assert string == "<test_configuration.empty_subclass_ConfigurationParser.<locals>.SubConfigurationParser object at 0x000000000000> on location here"

def test_sub_load_into_dict(empty_subclass_ConfigurationParser):
    """
    Test the not supported of load_into_dict.
    """
    with pytest.raises(NotImplementedError):
        conf = empty_subclass_ConfigurationParser("here")
        conf.load_into_dict(conf)

def test_sub_save_from_dict():
    """
    Test the not supported of load_into_dict.
    """
    with pytest.raises(NotImplementedError):
        conf = empty_subclass_ConfigurationParser()
        conf.save_from_dict(conf, conf)

