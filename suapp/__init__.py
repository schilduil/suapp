#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import importlib
import os.path
import platform
import sys

from suapp.jandw import *
from logdecorator import *


__author__  = "Bert Raeymaekers <bert.raeymaekers@schilduil.org>"
__version__ = "1.0.0.0"


class SuAppError(Exception):
    pass


class ModuleError(SuAppError):
    pass


class ConfigurationError(SuAppError):
    pass

    
class Config(object):
    pass

    
@loguse
def setFlow_depr(flow, appconfig):
    log = logging.getLogger(self.__module__)
    try:
        for (context, name, intag, objecttype) in appconfig.flowpoints:
            log.debug(":setFlow: Adding flow(%s) %s: Drone(%s, %s())" % (context, name, intag, objecttype))
            if context not in flow.flow:
                flow.flow[context] = {}
            if name in flow.flow[context]:
                log.warn("Duplicate flowpoint name %s in context %s, using the latest one!" % (name, context))
            # TODO: Forsee targets other than tkapp
            try:
                flow.flow[context][name] = jandw.Drone(intag, getattr(tkapp, objecttype)())
            except Exception as err:
                logging.getLogger(__name__).error(": setFlow : Unknown object type %s in tkapp (%s: %s)." % (objecttype, type(err), err))
                raise ConfigurationError("Unknown object type %s in tkapp (%s: %s)!" % (objecttype, type(err), err))
    except Exception as err:
        logging.getLogger(__name__).error(": setFlow : Error in <flow> tag (%s: %s)." % (type(err), err))
        raise ConfigurationError("Error in <flow> tag (%s: %s)!" % (type(err), err))
    return (appconfig.appname, appconfig.appshortname)

    
def convert_to_log_level(txt):
    # If it is already an int, return it.
    if type(txt) == type(10):
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
 
    def __init__(self, configuration):
        self.target_module = None
        self.configuration = configuration
        # First thing to do is setup the logging.
        self.configure_log()
        # Next import the UI target.
        self.import_target()
        ### JEEVES needs a self.flow! and and __init__(self, configuration = None) ###
        self.flow = Jeeves(self)
        self.configure_flow()

    def configure_log(self):
        log = logging.getLogger(self.__module__)
        # Logging not configured yet, so postponing log.debug(">configure_log()")
        try:
            if not "log" in self.configuration:
                self.configuration["log"] = {}
            filename = "~/.%s/log/suapp.log" % (self.configuration["shortname"])
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
            logging.basicConfig(filename = os.path.expanduser(filename), filemode = filemode, format = format, level = convert_to_log_level(level))
            # Putting out the delayed debug statement.
            log.debug(">configure_log() [DELAYED]")
            print("Logging to %s." % (os.path.expanduser(filename)))

            # Configuring the further modules logging settings.
            if "modules" in self.configuration["log"]:
                for module in self.configuration["log"]["modules"]:
                    if "level" in self.configuration["log"]["modules"][module]:
                        level = convert_to_log_level(self.configuration["log"]["modules"][module]["level"])
                        logging.getLogger("modules.%s" % (module)).setLevel(level)
        except ConfigurationError:
            # Re-raise
            raise
        except AttributeError as err:
            log.error("!SuApp.configure_log: Error in <log> tag (%s: %s)." % (type(err), err))
            raise ConfigurationError("Error in <log> tag (%s: %s)!" % (type(err), err))
        log.debug("<configure_log() %s" % (self.configuration["log"]))
    
    @loguse
    def import_target(self):
        if not "target" in self.configuration:
            targets = importlib.import_module("targets")
            # The default target is in targets/__init__ as default.
            self.configuration["target"] = targets.default
        self.target_module = "targets.%s" % (self.configuration["target"])
        globals()["ui"] = importlib.import_module(self.target_module)
        logging.getLogger(self.__module__).info("Target module: %s %s", self.target_module, ui)
        
    @loguse
    def parse_flow_line(self, line):
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
        simpletestingflow = { "START": Drone("START", ui.Application()) }
        return flow
        
        
    @loguse
    def configure_flow(self):
        if not "shortname" in self.configuration:
            self.configuration["shortname"] = "suapp"
        self.flow.flow[""] = self.read_flow("%s.flow" % self.configuration["shortname"])
        if len(self.flow.flow[""]) == 0:
            raise ConfigurationError("Could not load correct flow configuration.")
        if "modules" in self.configuration:
            for module in self.configuration["modules"]:
                subflow = self.read_flow(os.path.join("modules", "%s.flow" % (module)))
                self.flow.flow[module] = subflow

    @loguse
    def start(self):
        self.flow.start()

   
#
# MAIN: The root of all evil
#
if __name__ == "__main__":


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

    ## FOR TESTING NEW CONFIG BREAK EARLY
    #print("TEMPORARY END FOR CONFIG TEST")
    #sys.exit(0)

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

        ### START TEMPORARY TEST CODE ###
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
        ### END TEST ###

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

