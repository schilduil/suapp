#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import importlib
import os.path
import platform
import sys

import pony.orm

from suapp.jandw import *
from suapp.logdecorator import *
from suapp.moduleloader import *


class SuAppError(Exception):
    pass


class ModuleError(SuAppError):
    pass


class ConfigurationError(SuAppError):
    pass


class Config(object):
    pass


# Prepare for gettext
_ = lambda s: s


def do_locale(languages=None, domain=None, localedir=None):
    """
    Initializing gettext with the correct language.

    Returns false if it couldn't find anything. In that case it falls back to
    no translation.
    """
    import gettext
    import logging
    import os.path
    global _
    if not domain:
        domain = "suapp"
    if not languages:
        # Disable the translations.
        _ = lambda s: s
        return True
    if isinstance(languages, str):
        languages = [languages]
    if not localedir:
        localedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'locale')
    logging.getLogger(__name__).debug("Locale %s: %s" % (languages, gettext.find(domain, localedir=localedir, languages=languages, all=True)))
    try:
        trans = gettext.translation(domain, localedir=localedir, languages=languages)
        # This somehow doesn't work
        # trans.install()
        # So we have this alternative
        _ = trans.gettext
    except:
        logging.getLogger(__name__).warn("Locale for domain %s in languages %s not found. Falling back to default." % (domain, languages))
        _ = lambda s: s
        return False
    # Report our success.
    # We could use an Exception to signal failure but I prefer not to need a
    # try clause around a call to this function.
    return True


def do_all_locale(modules, languages=None):
    result = do_locale(language=languages)
    # TODO stuff for the modules.
    # result &= <module>.do_locale(language=languages)
    return result


def convert_to_log_level(txt):
    """
    Converts text to the actual log level.
    """
    # If it is already an int, return it.
    if isinstance(txt, int):
        return txt
    # Does it represent an int? If so return it.
    try:
        return int(txt)
    except:
        pass
    txt = txt.upper()
    if txt == "":
        return logging.NOTSET
    if txt == "CRITICAL":
        return logging.CRITICAL
    if txt == "DEBUG":
        return logging.DEBUG
    if txt == "ERROR":
        return logging.ERROR
    if txt == "FATAL":
        return logging.FATAL
    if txt == "INFO":
        return logging.INFO
    if txt == "WARN":
        return logging.WARNING
    if txt == "CRITICAL":
        return logging.WARNING
    if txt == "NOTSET":
        return logging.NOTSET
    if txt.startsWith("LEVEL "):
        try:
            return int(txt[6:])
        except:
            raise ConfigurationException("Log level is not a number: %s" % (txt))
    raise ConfigurationException("Unknow log level: %s" % (txt))


class SuApp(object):
    """
    The SuApp class represents a running application.
    """

    def __init__(self, configuration):
        """
        Initializing the application.

        Setting the configuration recieved.
        Configure the logging.
        Loading the UI target.
        Creating the Jeeves flow.
        Configure the flow.
        Configure the database and instanciating it.
        """
        self.target_module = None
        self.configuration = configuration
        # First thing to do is setup the logging.
        self.configure_log()
        # Next import the UI target.
        self.import_target()
        # JEEVES needs a self.flow! and and __init__(self, configuration = None)
        self.flow = Jeeves(self)
        self.configure_flow()
        # Import modlib libraries.
        self.load_modules()
        # DATABASE: pony.orm
        self.db = pony.orm.Database()
        try:
            self.db.bind(self.configuration['datasource']['type'], os.path.expanduser(self.configuration['datasource']['filename']), create_db=True)
        except KeyError:
            self.db.bind("sqlite", ":memory:")
        self.db.generate_mapping(create_tables=True)

    def configure_log(self):
        """
        Configuring the logging.

        The main logging but also all the module specific logging.
        """
        log = logging.getLogger(self.__module__)
        # Logging not configured yet, so postponing log.debug(">configure_log()")
        try:
            if "log" not in self.configuration:
                self.configuration["log"] = {}
            filename = "~/.%s/log/suapp.log" % (self.configuration["shortname"].lower())
            filemode = "w"
            level = "INFO"
            format = '%(asctime)s %(levelname)s %(name)s %(message)s'
            if "filename" in self.configuration["log"]:
                filename = os.path.expanduser(self.configuration["log"]["filename"])
            else:
                self.configuration["log"]["filename"] = filename
            if "filemode" in self.configuration["log"]:
                filemode = self.configuration["log"]["filemode"]
            else:
                self.configuration["log"]["filemode"] = filemode
            if "format" in self.configuration["log"]:
                format = self.configuration["log"]["format"]
            else:
                self.configuration["log"]["format"] = format
            if "level" in self.configuration["log"]:
                level = self.configuration["log"]["level"]
            else:
                self.configuration["log"]["level"] = level

            # Making sure the directory exists.
            os.makedirs(os.path.dirname(os.path.expanduser(filename)), exist_ok=True)
            # Starting the logging.
            logging.basicConfig(filename=os.path.expanduser(filename), filemode=filemode, format=format, level=convert_to_log_level(level))
            # Putting out the delayed debug statement.
            log.debug(">configure_log() [DELAYED]")
            print(_("Logging to %s.") % (os.path.expanduser(filename)))

            # Configuring the further modules logging settings.
            if "modules" in self.configuration["log"]:
                for module in self.configuration["log"]["modules"]:
                    module_logger = logging.getLogger("modules.%s" % (module))
                    if "level" in self.configuration["log"]["modules"][module]:
                        level = convert_to_log_level(self.configuration["log"]["modules"][module]["level"])
                        module_logger.setLevel(level)
                    if "filename" in self.configuration["log"]["modules"][module]:
                        log.info("!Logging modules.%s to %s" % (module, self.configuration["log"]["modules"][module]["filename"]))
                        module_logger.propagate = False
                        module_logger.addHandler(logging.FileHandler(os.path.expanduser(self.configuration["log"]["modules"][module]["filename"])))
        except ConfigurationError:
            # Re-raise
            raise
        except AttributeError as err:
            log.error("!SuApp.configure_log: Error in <log> tag (%s: %s)." % (type(err), err))
            raise ConfigurationError("Error in <log> tag (%s: %s)!" % (type(err), err))
        log.debug("<configure_log() %s" % (self.configuration["log"]))

    @loguse
    def import_target(self):
        """
        Import the UI target as ui.
        """
        if "target" not in self.configuration:
            targets = importlib.import_module("suapp.targets")
            # The default target is in targets/__init__ as default.
            self.configuration["target"] = targets.default
        self.target_module = "suapp.targets.%s" % (self.configuration["target"])
        globals()["ui"] = importlib.import_module(self.target_module)
        logging.getLogger(self.__module__).info("Target module: %s %s", self.target_module, ui)

    @loguse
    def parse_flow_line(self, line):
        """
        Parse one flow line.
        """
        comment = ""
        line = line.split("#", 1)
        content = line[0].strip()
        if len(line) > 1:
            comment = line[1].strip()
        if len(content) > 0:
            (out, fullin) = content.split(":", 1)
            out = out.strip()
            fullin = fullin.strip()
            (target, intag) = fullin.rsplit(".", 1)
            logging.getLogger(self.__module__).debug("Flow element: %s: %s.%s (%s)", out, target, intag, comment)
            return (out, intag, target)
        return (None, None, None)

    @loguse
    def read_flow(self, flowfile):
        """
        Reading the flow file.
        """
        flow = {}
        # 1. Look starting from the install location.
        installpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        # 2. Look starting from the directory of the config file (if different).
        configpath = os.path.dirname(self.configuration["self"])
        logging.getLogger(self.__module__).debug("!read_flow from install path: %s" % installpath)
        logging.getLogger(self.__module__).debug("!read_flow from configuration path: %s" % configpath)
        try:
            with open(os.path.join(installpath, flowfile)) as fh:
                for line in fh:
                    (out, intag, objecttype) = self.parse_flow_line(line)
                    if out:
                        flow[out] = jandw.Drone(intag, getattr(ui, objecttype)())
        except IOError as e:
            logging.getLogger(self.__module__).debug(e)
        except OSError as e:
            logging.getLogger(self.__module__).debug(e)
        if not configpath == installpath:
            try:
                with open(os.path.join(configpath, flowfile)) as fh:
                    for line in fh:
                        (out, intag, objecttype) = self.parse_flow_line(line)
                        if out:
                            flow[out] = jandw.Drone(intag, getattr(ui, objecttype)())
            except IOError as e:
                logging.getLogger(self.__module__).debug(e)
            except OSError as e:
                logging.getLogger(self.__module__).debug(e)
        simpletestingflow = {"START": Drone("START", ui.Application())}
        return flow

    @loguse
    def configure_flow(self):
        """
        Configures the flow.
        """
        if "shortname" not in self.configuration:
            self.configuration["shortname"] = "SuApp"
        self.flow.flow[""] = self.read_flow("%s.flow" % self.configuration["shortname"].lower())
        if len(self.flow.flow[""]) == 0:
            raise ConfigurationError("Could not load correct flow configuration.")
        if "modules" in self.configuration:
            for module in self.configuration["modules"]:
                subflow = self.read_flow(os.path.join("modules", "%s.flow" % (module)))
                self.flow.flow[module] = subflow

    @loguse
    def load_modules(self):
        """
        Start the application.
        """
        # Getting the modules to load form the configurarion.
        modules_to_import = self.configuration["modules"].keys()
        app_name = self.configuration["shortname"].lower()
        # If no modules, at least do base.
        if not modules_to_import:
            modules_to_import = ['base']
        logging.getLogger(__name__).debug("Modules to load: %s" % (modules_to_import))
        # TODO: I have to find out why I need this next line.
        #gl = globals()
        scope = {}
        for mod in modules_to_import:
            import_modlib(app_name, mod, scope)
        logging.getLogger(__name__).info("Modules loaded: %s" % (modules))

    @loguse
    def start(self):
        """
        Start the application.
        """
        self.flow.start()


#
# MAIN: The root of all evil
#
if __name__ == "__main__":
    #
    # This was some test code, but I'm not sure it still works.
    #

    log = logging.getLogger(__name__)

    # Run with a configuration
    try:
        appconfig = config.get_config(xmlfilename)
    except config.ConfigurationError as err:
        log.error("%s" % (err))
        print("%s" % (err))
        sys.exit(1)

    # Getting all the configuration from the appconfig
    flow = Jeeves()
    try:
        log.info("Running on %s %s version %s on %s %s on %s (%s)" % (platform.python_implementation(), platform.python_build(), platform.python_version(), platform.system(), platform.release(), platform.machine(), platform.processor()))
        log.debug("Config (%s):\n%s" % (xmlfilename, appconfig))
        (name, shortname) = setFlow_depr(flow, appconfig)
        dataDefinitions = appconfig.data_definition
    except config.ConfigurationError as err:
        log.error("%s" % (err))
        print("%s" % (err))
        sys.exit(1)

    # A poor man's nested context manager, which in this case isn't too
    # bad since we sys.exit(2) anyway so no lingering resources anyway.
    # Nevertheless it should behave nicely on error.
    tables = {}
    indtable = None
    try:
        for table in dataDefinitions['tables']:
            log.debug("Table %s: %s" % (table, dataDefinitions['tables'][table]))
            tables[table] = (factory.tableFactory(dataDefinitions['tables'][table], table))
        for gen in tables:
            print("\nGoing to open %s (%s)" % (gen, tables[gen]))
            tables[gen].__enter__()

        # == START TEMPORARY TEST CODE == #
        indtable = tables['organism']
        perstable = tables['person']
        indtable.setFor('GOc', dict(gender=1, bandcode=dict(breeder='FS2', year='06', sequence=654), breeder='Frank Silva', status=-128))
        indtable.setFor('GOh', dict(gender=2, bandcode=dict(breeder='FS2', year='06', sequence=774), breeder='Frank Silva', status=-128))
        indtable.setFor('MCc', dict(gender=1, bandcode=dict(breeder='FS2', year='06', sequence=870), breeder='Frank Silva', status=-128))
        indtable.setFor('MCh', dict(gerder=2, bandcode=dict(breeder='FS2', year='06', sequence=559), breeder='Frank Silva', status=-128))
        indtable.setFor('(131GAOC)298', dict(gender=1, bandcode=dict(issuer='BGC', breeder='BR23', year='11', sequence=298), breeder='Bert Raeymaekers', status=1))
        indtable.setFor('(302267)343', dict(gender=2, bandcode=dict(issuer='BGC', breeder='BR23', year='12', sequence=343), breeder='Bert Raeymaekers', status=1))
        perstable.setFor('1', dict(firstname="Bert", lastname="Raeymaekers", email="br23@schilduil.org", bandcode="BR23"))
        perstable.setFor('2', dict(firstname="Stefaan", lastname="Buggenhout", bandcode="SB18"))
        log.debug("All the (active) members:")
        for individual in indtable:
            log.debug("\tIndividual %s" % (individual))
        log.debug("State: %s" % indtable.state())
        goc = indtable['GOc']
        print("\nGetting GOc: %s %r %s" % (id(goc), goc, goc))
        goc = indtable['GOc']
        print("\nGetting GOc: %s %r %s" % (id(goc), goc, goc))
        # == END TEST == #

        # Pass the application configuration
        flow.start({'config': appconfig, 'name': name, 'shortname': shortname, 'tables': tables})
    except Exception as err:
        log.error("%s" % (err))
        print(err)
        raise err
        sys.exit(2)
    finally:
        for gen in tables:
            tables[gen].__exit__(None, None, None)

    print("Bye.")
