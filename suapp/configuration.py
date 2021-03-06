#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from collections.abc import MutableMapping


"""
Module for reading and writing the configuration.

USAGE:
    configuration.get_configuration([location], [source_type], [file_type], [**kwargs]):
        location: file name with path
        source_type: see below
        file_type: see below
        kwargs: extra parameters (depends on the source_type)

It supports different source types:
    file: local file.
    web: file on the web (e.g. http)

It supports different file types:
    json (based on the json module)
    xml (using xmltodict by Martin Blech)
    yaml (using pyyaml by pyyaml.org)
    cfg (based on the configparser module)
"""


class Configuration(MutableMapping):
    """
    Dict like class containing the configuration.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the dictionary the same as a real dict.
        """
        self.store = dict()
        if args or kwargs:
            self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        """
        Get an item form the configuration dict.
        """
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        """
        Set an item in the configuration dict.
        """
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        """
        Remove an item from the configuration dict.
        """
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        """
        Return the iterator of the dictonary.
        """
        return iter(self.store)

    def __len__(self):
        """
        Return the lenght of the dictionary.
        """
        return len(self.store)

    def __keytransform__(self, key):
        """
        Transforms the key.
        """
        return key

    # -- We want it to output like a dict --

    def __repr__(self):
        """
        Represent itself as a dict.
        """
        return self.store.__repr__()

    # -- Configuration specific methods: load, save & close. --

    def load(self):
        """
        Reloads the configuration - does nothing in Configuration.

        Normally only called once, usually by __enter__ if you're using the with statement.
        """
        pass

    def save(self):
        """
        Call this when wanting to do an explicit save of the configuration.

        It can be called multiple times in the live time of the object.
        It must raise a NotImplementedError if this is not supported for your
        type of configuration.
        """
        raise NotImplementedError("Save is not implemented on ")

    def close(self):
        """
        Always call this after you've done with a configuration.

        Here it is just a place holder for subclasses that need to clean up
        after itself.
        """
        pass

    # -- Contect manager --

    def __enter__(self):
        """
        Implementing it as a context manager: loading the configuration.
        """
        self.load()
        return self

    def __exit__(self, *args):
        """
        Implementing it as a context manager: call close.
        """
        self.close()


class SplitConfiguration(Configuration):
    """
    Receives a list of Configuration instances where the extra ones are backups.

    The first configuration instance in the list is the main one and the only
    one that is used for writing the configuration. If it can't be loaded the
    first backup will be loaded (and so on) and that configuration is
    immediately saved to the main configuration.

    After the initial load this behaves just like there is only the main
    configuration instance. Actually, if the main configuration is good the
    backups are never used.
    """

    def __init__(self, configurations):
        """
        Initializes a split configuration from different configurations.
        """
        super().__init__()
        self.main = None
        backup = []
        for config in configurations:
            # First one is the main one.
            if self.main is None:
                self.main = config
            else:
                backup.append(config)
        if len(backup) == 0:
            self.backup = None
        elif len(backup) == 1:
            self.backup = backup[0]
        else:
            self.backup = SplitConfiguration(backup)

    def load(self):
        """
        Load the configuration: first try the main.
        """
        try:
            # Try to load the main configuration.
            self.main.load()
        except:
            # That didn't work, so trying the backup.
            if self.backup is not None:
                # Loading from the backup and saving it to the main configuration.
                self.backup.load()
                self.main.update(self.backup)
                self.main.save()
            else:
                # No backup, re-raising the original exception.
                raise

    def save(self):
        """
        Save the configuration: always to the main.
        """
        self.main.save()

    def __enter__(self):
        """
        Return the context manager of the main.
        """
        self.load()
        # Once the initial load is done, only the main configuration matters.
        return self.main

    def __getitem__(self, key):
        """
        Get the item.
        """
        return self.main.__getitem__(key)

    def __setitem__(self, key, value):
        """
        Set the item.
        """
        return self.main.__setitem__(key, value)

    def __delitem__(self, key):
        """
        Remove the item.
        """
        return self.main.__del__(key)

    def __len__(self):
        """
        Return the lenght.
        """
        return self.main.__len__()

    def __repr__(self):
        """
        Represent as the main.
        """
        return self.main.__repr__()

    def clear(self):
        """
        Clear the main.
        """
        return self.main.clear()

    def copy(self):
        """
        Returns a copy
        """
        return self.main.copy()

    def has_key(self, key):
        return self.main.has_key(key)  # noqa

    def pop(self, key, d=None):
        return self.main.pop(key, d)

    def update(self, *args, **kwargs):
        return self.main.update(*args, **kwargs)

    def keys(self):
        return self.main.keys()

    def values(self):
        return self.main.values()

    def items(self):
        return self.main.items()

    def pop(self, *args):
        return self.main.pop(*args)

    def __cmp__(self, item):
        return self.main.__cmp__(item)

    def __contains__(self, item):
        return self.main.__contains__(item)

    def __iter__(self):
        return self.main.__iter__()

    def __unicode__(self):
        return self.main.__unicode__()


class ConfigurationParser:
    """
    Dummy root of all configuration parser classes.
    """

    def __init__(self, location, **options):
        """
        Initialize with a location.
        """
        self.location = location
        self.options = options

    @staticmethod
    def infer_type(value):
        if value is None:
            return {}
        try:
            value = int(value)
        except:
            try:
                value = float(value)
            except:
                pass
        return value

    def load_into_dict(self, configuration):
        """
        Must be overwritten in the subclass.
        """
        if isinstance(self, ConfigurationParser):
            raise NotImplementedError("ConfigurationParser is a dummy.")
        else:
            raise NotImplementedError(
                "Load is not implemented in %s." % (self.__class__.__name__)
            )

    def save_from_dict(self, configuration):
        """
        Must be overwritten in the subclass.
        """
        if isinstance(self, ConfigurationParser):
            raise NotImplementedError("ConfigurationParser is a dummy.")
        else:
            raise NotImplementedError(
                "Save is not implemented in %s." % (self.__class__.__name__)
            )

    def __str__(self):
        """
        String representation of the parser.
        """
        return super().__str__() + " on location %s" % (self.location)


class JsonConfigurationParser(ConfigurationParser):
    """
    Parses a json file.
    """

    def load_into_dict(self, configuration):
        """
        Parsing a json file and updating the configuration.
        """
        import json

        json_conf = None
        with open(self.location, encoding="utf-8") as data_file:
            json_conf = json.load(data_file)
        configuration.update(json_conf)

    def save_from_dict(self, configuration):
        """
        Saving the configuration again.
        """
        import json

        with open(self.location, "w", encoding="utf-8") as data_file:
            json.dump(
                dict(configuration),
                data_file,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )


class YamlConfigurationParser(ConfigurationParser):
    """
    Parses a yaml file.
    """

    def load_into_dict(self, configuration):
        """
        Parsing a yaml file and updating the configuration.
        """
        import yaml

        configuration.update(
            yaml.load(
                open(self.location, "r", encoding="utf-8"), Loader=yaml.SafeLoader
            )
        )

    def save_from_dict(self, configuration):
        """
        Saving the configuration again to the yaml.
        """
        import yaml

        yaml.dump(dict(configuration), open(self.location, "w", encoding="utf-8"))


class XmlConfigurationParser(ConfigurationParser):
    """
    Parses an XML file.
    """

    def load_into_dict(self, configuration):
        """
        Parsing an xml file and updating the configuration.
        """
        import xmltodict

        configuration.update(
            xmltodict.parse(
                open(self.location, "rb"),
                encoding="utf-8",
                postprocessor=lambda path, key, value: (
                    key,
                    ConfigurationParser.infer_type(value),
                ),
            )["suapp"]
        )

    def save_from_dict(self, configuration):
        """
        Saving the configuration again to xml.
        """
        import xmltodict

        xmltodict.unparse(
            {"suapp": dict(configuration)},
            open(self.location, "wb"),
            encoding="utf-8",
            pretty=True,
        )


class CfgConfigurationParser(ConfigurationParser):
    """
    Parses a configuration in the configparser format.
    """

    def configuration_to_flat_dict(self, configuration, prefix=None):
        """
        Flattens the configuration from multiple levels to one.

        From:
            {"a": {"b": {"c": "value"}}}
        To:
            {"a.b.c": "value"}
        """
        if not prefix:
            prefix = []
        config_flat = dict()
        for key, value in configuration.items():
            new_prefix = list(prefix)
            new_prefix.append(key)
            if type(value) == type(config_flat):
                new_prefix = list(prefix)
                new_prefix.append(key)
                config_flat.update(
                    self.configuration_to_flat_dict(value, prefix=new_prefix)
                )
            else:
                config_flat[".".join(new_prefix)] = value
        if not config_flat:
            # Nothing put into it, so creating an empty dummy sub prefix entry.
            config_flat[".".join(prefix) + "."] = ""
        return config_flat

    def configuration_to_configparser(self, configuration):
        """
        Converts the configuration to a configuration for configparser.

        From:
            {"a": {"b": {"c": "value"}}}
        To:
            [a.b]
            c = value
        """
        import configparser

        config_parser = configparser.RawConfigParser()
        config_flat = self.configuration_to_flat_dict(configuration)
        for fullkey, value in config_flat.items():
            try:
                (section, key) = fullkey.rsplit(".", 1)
            except ValueError:
                section = ""
                key = fullkey
            try:
                if section != "":
                    config_parser.add_section(section)
            except configparser.DuplicateSectionError:
                # Ignore
                pass
            if key:
                config_parser.set(section, key, value)
        return config_parser

    def load_into_dict(self, configuration):
        """
        Reads in the config file.
        """
        import configparser

        config = configparser.ConfigParser()
        config.read_file(open(self.location, encoding="utf-8"))
        defaults = config.defaults()
        for key, value in defaults.items():
            configuration[key] = ConfigurationParser.infer_type(value)
        for section in config.sections():
            section_path = section.split(".")
            current = configuration
            for step in section_path:
                if step not in current:
                    current[step] = {}
                current = current[step]
            for key in config.options(section):
                raw = self.options.get("raw", True)
                value = config.get(section, key, raw=raw)
                if self.options.get("sparse", True):
                    if key in defaults:
                        if defaults[key] == value:
                            continue
                current[key] = ConfigurationParser.infer_type(value)

    def save_from_dict(self, configuration):
        """
        Saves the configuration to a config file.

        It uses the write function on the configparser that needs the file handle.
        """
        config_parser = self.configuration_to_configparser(configuration)
        with open(self.location, "w", encoding="utf-8") as config_parser_file_handle:
            config_parser.write(config_parser_file_handle)


def get_configuration_parser(location, file_type, **options):
    """
    Returns the parser based on the file type.
    """
    if file_type == "json":
        return JsonConfigurationParser(location, **options)
    elif file_type == "cfg":
        return CfgConfigurationParser(location, **options)
    elif file_type == "xml":
        return XmlConfigurationParser(location, **options)
    elif file_type == "yaml":
        return YamlConfigurationParser(location, **options)
    else:
        raise NotImplementedError("Unknown file type to parse: %s." % (file_type))


class FileConfiguration(Configuration):
    """
    Loads and saves the configuration from the file system.
    """

    def __init__(self, location, file_type=None, **options):
        """
        Initializing the parser depending on the file type.
        """
        super().__init__()
        # Trying to infer the file type if not given.
        if not file_type:
            if location.lower().endswith(".json"):
                file_type = "json"
            elif location.lower().endswith(".xml"):
                file_type = "xml"
            elif location.lower().endswith(".cfg"):
                file_type = "cfg"
            elif location.lower().endswith(".ini"):
                file_type = "cfg"
            elif location.lower().endswith(".yml"):
                file_type = "yaml"
            elif location.lower().endswith(".yaml"):
                file_type = "yaml"
            else:
                file_type = "???"
        # Based on the file type.
        self.parser = get_configuration_parser(location, file_type, **options)

    def load(self):
        """
        Have the parser read in the configuration.
        """
        self.parser.load_into_dict(self)

    def save(self):
        """
        Have the parser write out the configuration.
        """
        self.parser.save_from_dict(self)


class WebConfiguration(Configuration):
    """
    Loads the configuration from the web.
    """

    def __init__(self, url, **options):
        """
        Initializes with an url
        """
        super().__init__()
        self.url = url
        self.options = options

    def load(self):
        """
        Downloading the web resource to a temporary file and reading it in.
        """
        import os
        import shutil
        import tempfile
        import urllib.request

        file_type = None
        file_type = self.url.rsplit(".", 1)[1]
        if "/" in file_type:
            # The URL doesn't seem to contain file at the end so this was wrong.
            file_type = None
        file_name = None
        try:
            # Download the file from `url` and save it locally under `file_name`:
            (os_level_handle, file_name) = tempfile.mkstemp(suffix=".%s" % (file_type))
            os.close(os_level_handle)
            with urllib.request.urlopen(self.url) as response, open(
                file_name, "wb"
            ) as out_file:
                shutil.copyfileobj(response, out_file)
            # Using FileConfiguration on the temporary file to do the real stuff.
            file_conf = FileConfiguration(file_name, file_type, **self.options)
            file_conf.load()
            self.update(file_conf)
        except:
            # Re-raising.
            raise
        finally:
            try:
                # Always try to delete the temporary file.
                os.remove(file_name)
            except:
                pass

    def save(self):
        """
        Saving of the configuration on a WebCOnfiguration is not supported.

        TODO EXTRA: we could try to do a HTTP PUT or stuff similar.
        """
        raise NotImplementedError("Save is not implemented on WebConfiguration.")


def get_configuration(location=None, source_type=None, file_type=None, **kwargs):
    """
    Returns the configuration object for the location.

    Possible source types are: http, file. If not specified it tries
    to infer the type if it is 'http' and else defaults to 'file'.

    The file type is only used when the source type is 'file'.
    """
    # Inferring source type if not given.
    if not source_type:
        if not location:
            return Configuration(**kwargs)
        elif isinstance(location, dict):
            return Configuration(**location)
        elif isinstance(location, list):
            configuration_list = []
            for sub_location in location:
                if isinstance(sub_location, Configuration):
                    configuration_list.append(sub_location)
                else:
                    configuration_list.append(
                        get_configuration(location=sub_location, **kwargs)
                    )
            return SplitConfiguration(configuration_list)
        elif location.lower().startswith("http://"):
            source_type = "http"
        elif location.lower().startswith("https://"):
            source_type = "http"
        else:
            source_type = "file"
    # Getting the correct Configuration object.
    if source_type == "http":
        return WebConfiguration(location, **kwargs)
    elif source_type == "file":
        return FileConfiguration(location, file_type=file_type, **kwargs)
    else:
        raise IOError("Unknown source type %s." % (source_type))
