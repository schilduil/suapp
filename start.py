#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Starts up a SuApp application.

Optional parameters:
    -c <json configuration file or path>
        filename (without path): look for it in the default location.
        filename with path: take it as it is.
        path of existing directory: look for suapp.json in there.
    -t <target>: tk [DEFAULT], console, web, ...
    Other config parameters you want to overwrite in the form of
    "a.b.c=VALUE,a.d.e.f=1".
    
This
    - Reads in the configuration,
    - Sets the logging,
    - Loads the flow configurations and
    - Calls START to start the application.
"""

# TARGET:
#       LocalWeb: run SimpleHTTPServer and open a browser to it.
#       TK: run a local TK app.
#       TKWeb: Open a TK app getting the info (json) from a specific URL.
#       TKLocalWeb: run a SimpleHTTPServer and open a TKWeb.

import argparse
import logging
import os.path
import sys

import suapp


def configuration_to_flat_dict(configuration, prefix = None):
    if not prefix:
        prefix = []
    config_flat = dict()
    for key,value in configuration.items():
        new_prefix = list(prefix)
        new_prefix.append(key)
        if type(value) == type(config_flat):
            new_prefix = list(prefix)
            new_prefix.append(key)
            config_flat.update(configuration_to_flat_dict(value, prefix = new_prefix))
        else:
            config_flat['.'.join(new_prefix)] = value
    #print("%s: %s - %s" % (prefix, configuration, config_flat)) # DELME
    return config_flat


def configuration_to_configparser(configuration):
    import configparser
    config_parser = configparser.RawConfigParser()
    config_flat = configuration_to_flat_dict(configuration)
    for fullkey,value in config_flat.items():
        try:
            (section,key) = fullkey.rsplit('.',1)
        except ValueError:
            section = ""
            key = fullkey
        #print("[%s] %s: %s - %s" % (section, key, value, fullkey))
        try:
            if section != "":
                config_parser.add_section(section)
        except configparser.DuplicateSectionError:
            # Ignore
            pass
        config_parser.set(section, key, value)
    return config_parser


def read_conf_json(jsonfilename):
    import json
    try:
        with open(jsonfilename) as data_file:    
            return json.load(data_file)
    except IOError as e:
        print()
        print("Could not load the configuration: %s." % (e))
        exit(1)
    except ValueError as e:
        print()
        print("Could not parse the configuration: %s." % (e))
        exit(1)


def read_conf(filename):
    if filename.endswith(".json"):
        configuration = read_conf_json(filename)
        try:
            import os.path
            import tempfile
            config_parser = configuration_to_configparser(configuration)
            with open(os.path.join(tempfile.gettempdir(),'suapp.cfg'), 'w') as config_parser_file_handle:
                config_parser.write(config_parser_file_handle)
        except:
            # Ignore if this fails, just for debugging.
            pass
        return configuration


def update_conf(configuration, option_string):
    if not option_string:
        return
    options = option_string.split(",")
    for option in options:
        (key,value) = option.split("=",1)
        context = key.split(".")
        subconfig = configuration
        while len(context) > 1 and (context[0]) in subconfig:
            subconfig = subconfig[context[0]]
            context.pop(0)
        subconfig[context[0]] = value

        
if __name__ == "__main__":
    # By default the json configuration file is in the local directory and is
    # called suapp.json.
    # But this can be overwritten by passing a -c parameter passing the 
    # filename, path or the full json file location.

    parser = argparse.ArgumentParser(description='Start a SuApp application.')
    parser.add_argument('-o', '--options', help="[key=value]* overrides to the configuration")
    parser.add_argument('-c', '--configuration', help="path or filename of the configuration file (json)", default="suapp.json")
    parser.add_argument('-t', '--target', help="target user interface")
    args = parser.parse_args()

    print("Configuration file: %s" % (args.configuration))
    print("User interface target: %s" % (args.target))
    print("Options: %s"% (args.options))

    jsonfilename = 'suapp.json'
    if args.configuration:
        if os.path.isdir(args.configuration):
            # An existing directory is passed.
            jsonfilename = os.path.join(args.configuration, jsonfilename)
        elif args.configuration == os.path.basename(args.configuration):
            # Going to the path of the start.py script and
            # And hence if the config file is relative it will originate from here.
            os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
            jsonfilename = os.path.realpath(args.configuration)
        else:
            jsonfilename = args.configuration
    else:
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
        jsonfilename = os.path.realpath(jsonfilename)

    print("Effective configuration file: %s" % (jsonfilename))
    
    configuration = read_conf(jsonfilename)
    configuration["self"] = jsonfilename
    update_conf(configuration, args.options)
    if args.target:
        configuration["target"] = args.target
    
    try:    
        app = suapp.SuApp(configuration)
        app.start()
        print("Bye.")
    except Exception as e:
        try:
            logging.getLogger(__name__).fatal("Unexpected end of SuApp: %s" % (e))
        finally:
            print("Unexpected end of SuApp!")
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info() 
            traceback.print_exception(exc_type, exc_value, exc_traceback)

