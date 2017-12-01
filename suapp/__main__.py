#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Starts up a SuApp application.

Optional parameters:
    -c <json configuration file or path>
        filename (without path): look for it in the default location.
        filename with path: take it as it is.
        path of existing directory: look for suapp.json in there.
    -t <target>: tk [DEFAULT], test, localweb, ...
    Other config parameters you want to overwrite in the form of
    "a.b.c=VALUE,a.d.e.f=1".

This
    - Reads in the configuration,
    - Sets the logging,
    - Loads the flow configurations and
    - Calls START to start the application.
"""


import argparse
import locale
import logging
import os.path
import sys

import suapp
import suapp.configuration


def update_conf(configuration, option_string):
    """
    Updates the configuration with different options.

    The option_string is a comma separate list of configuration key=value pairs.
    Dots in the key reflect the depth in the configuration.

    From:
        a.b.c=value
    To:
        {"a": {"b": "c": "value"}}}
    """
    if not option_string:
        return
    options = option_string.split(",")
    for option in options:
        (key, value) = option.split("=", 1)
        context = key.split(".")
        subconfig = configuration
        while len(context) > 1:
            if (context[0]) not in subconfig:
                subconfig[context[0]] = {}
            subconfig = subconfig[context[0]]
            context.pop(0)
        # Transforming so clear booleans from str.
        try:
            value = {
                    'false': False,
                    'true': True
            }.get(value.lower(), value)
            value = int(value)
        except ValueError as e:
            try:
                value = float(value)
            except ValueError as ve:
                pass
        subconfig[context[0]] = value


if __name__ == "__main__":
    # By default the json configuration file is in the local directory and is
    # called suapp.json.
    # But this can be overwritten by passing a -c parameter passing the
    # filename, path or the full json file location.

    languages = set([locale.getlocale()[0], locale.getlocale()[0].split('_')[0]])
    suapp.do_locale(languages)

    parser = argparse.ArgumentParser(description=suapp._('Start a SuApp application.'))
    parser.add_argument('-l', '--lang', help=suapp._("language, use 'none' if you don't want a language setting. If not set it infers the language from the environment setting."), default=locale.getlocale()[0])
    parser.add_argument('-o', '--options', help=suapp._("[key=value]* overrides to the configuration"))
    parser.add_argument('-c', '--configuration', help=suapp._("path or filename of the configuration file (json)"), default="suapp.json")
    parser.add_argument('-t', '--target', help=suapp._("target user interface"))
    args = parser.parse_args()

    if args.lang.lower() == 'none':
        suapp.do_locale()
    else:
        languages = set([args.lang, args.lang.split('_')[0]])
        suapp.do_locale(languages)

    print(suapp._("Taal: %s") % (args.lang))
    print(suapp._("Configuration file: %s") % (args.configuration))
    print(suapp._("User interface target: %s") % (args.target))
    print(suapp._("Options: %s") % (args.options))

    jsonfilename = 'suapp.json'
    json_backup = 'https://raw.githubusercontent.com/schilduil/suapp/master/suapp.json'
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

    print(suapp._("Effective configuration file: %s") % (jsonfilename))
    print(suapp._("Backup initial configuration: %s") % (json_backup))

    config = suapp.configuration.get_configuration([jsonfilename, json_backup])
    config.load()
    config["self"] = jsonfilename
    update_conf(config, args.options)
    if args.target:
        config["target"] = args.target

    try:
        # Instanciating the application
        app = suapp.SuApp(config)
        app.start()
        print(suapp._("Bye."))
    except Exception as e:
        try:
            logging.getLogger(__name__).fatal(suapp._("Unexpected end of SuApp: %s") % (e))
        finally:
            print(suapp._("Unexpected end of SuApp!"))
            import traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
