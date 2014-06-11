# coding=utf-8

from __future__ import with_statement

import subprocess
import os.path
import sys
import ConfigParser
import time

import logClient

DEFAULT_CONFIG = "default.cfg"

class ProjConf(object):
    cfg = None
    sim_path = None
    config_file = None
    # Stores section:key pairs describing the unknown options for logging.
    def __init__(self, config_file, sim_path = None):
        """Initializes this module to use a specific configuration file

        config_file is the path to the configuration file.
        sim_path sets the project directory in which the simulations
        will take place and is generated if None, but not written or
        created in any form.
        """
        self.unrecognized_options = {}
        self.config_file = config_file
        self._parse_config_file(DEFAULT_CONFIG, self.config_file)

        if sim_path is None:
            self.sim_path = self.generate_output_path()
        else:
            self.sim_path = normPath(sim_path)
    #-----------------------------------------------------------
    def get(self, key, section = None):
        """Returns the value stored in the config.

        Raises an exception if not found.
        The default section is "Global".
        See getd() for a non throwing version.
        """
        if section is None: section = "Global"
        return self.cfg.get(section, key)
    #-----------------------------------------------------------
    def get_int(self, key, section = None):
        """Syntactic sugar for int(get(...))
        """
        return int(self.get(key, section))
    #-----------------------------------------------------------
    def get_float(self, key, section = None):
        """Syntactic sugar for float(get(...))
        """
        return float(self.get(key, section))
    #-----------------------------------------------------------
    def get_list(self, key, section = "Global"):
        """Parses value as comma separated list and returns the
        list of strings
        """
        string = self.get(key, section).strip()
        l = string.lstrip("[").rstrip("]").split(",")
        return [i.strip() for i in l]
    #-----------------------------------------------------------
    def getd(self, key, section = None, default = None):
        """Returns the value stored in the config or the default.

        See get() for a throwing version.
        """
        if section is None: section = "Global"
        if self.cfg.has_option(section, key):
            return self.cfg.get(section, key)
        return default
    #-----------------------------------------------------------
    def getd_int(self, key, section = None, default = 0):
        """Syntactic sugar for int(getd(...))
        """
        return int(self.getd(key, section, default))
    #-----------------------------------------------------------
    def getd_float(self, key, section = None, default = 0.0):
        """Syntactic sugar for float(getd(...))
        """
        return int(self.getd(key, section, default))
    #-----------------------------------------------------------
    def get_path(self, key, section = None):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current working directory,
        not the sim_path. Use get_local_path() for a variant
        relative to the simulation directory.
        """
        return normPath(self.get(key, section))

    #-----------------------------------------------------------
    def get_local_path(self, key, section = None):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current sim_path for this
        function. Use get_path() for a variant relative to the
        script invokation.
        """
        return self.localPath(self.get(key, section))
    #-----------------------------------------------------------
    def localPath(self, *args):
        """Returns a normalized path, with the concatenated
        args. 

        Takes one or several node names or relative paths
        and assumes they are local to the simulation directory
        for this run (maybe a temporary directory).
        NOTE: when an absolute path is given, all relative paths
        before are ignored.
        """
        return normPath(self.sim_path, *args)

    #-----------------------------------------------------------
    def generate_output_path(self):
        """Generates a timestamped path string, but does not create any directories.
        """
        result_folder = time.strftime("%Y-%m-%d_%H-%M-%S-") \
                        + self.getd("result_affix", default="result")
        output_path = normPath(self.get_path("result_directory"),
                                        result_folder)
        return output_path
    #-----------------------------------------------------------
    def set_sim_path(self, sim_path):
        """Changes the sim_path in which the simulations should run.

        NOTE: Changing this variable after starting the simulation
        should NEVER be done, as other modules depend on this path
        containing buffer and project files
        """
        self.sim_path = normPath(sim_path)
    #-----------------------------------------------------------
    def parseProjectConfig(self):
        values = {}
        filename = self.get_local_path("projectConfig")
        with open(filename, 'r') as config:
            c = 0 #counter
            for line in config:
                line = line.strip()
                c = c+1
                if c == 1:
                    values.update(proj_name = line)
                elif c == 2:
                    values.update(proj_path = line)
                elif c == 3:
                    values.update(log_server_port = int(line))
        return values
    #-----------------------------------------------------------
    def write_project_config(self, log_server_port):
        proj_name = "Pyr_" + self.get("mode", "Simulation")
        proj_path = proj_name+"/"+proj_name+".ncx"
        filename = self.get_local_path("projectConfig")
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError, exception:
            if exception.errno != errno.EEXIST:
                raise
        with open(filename, "w") as config:
            config.write(str(proj_name) + "\n"
                         + str(proj_path) + "\n"
                         + str(log_server_port) + "\n")
    #-----------------------------------------------------------
    def parseIndexFile(self):
        """Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!"""
        filenameIndex = self.get_local_path("candidateIndex")
        with open(filenameIndex, "r") as indexFile:
            idx = []
            val = 0
            for line in indexFile:
                try:    
                    val=int(line.strip())
                    idx.append(val)
                except:
                    pass
            return idx
    #-----------------------------------------------------------
    def invokeSimulation(self, type):
        """Starts the command ind args[0] and passes it the remaining entries.

        type is the string passed to MultiSim.py as the --type parameters.
        """
        arg_list = ["-python", normPath("GenAlg/Programm/MultiSim.py"),
                    "--config", self.config_file,
                    "--sim-directory", self.sim_path,
                    "--type", type]
        if sys.platform == "win32":
            externesProgramm = os.path.normpath(os.path.join(self.get("installPath", "NeuroConstruct"), "NC.bat"))
            p = subprocess.Popen( externesProgramm + " " + " ".join(args) )
            p.wait()
        else:
            subprocess.check_call([os.path.join(self.get("installPath", "NeuroConstruct"), "nC.sh")] + arg_list)
    #-----------------------------------------------------------
    def getClientLogger(self, logger_name, log_server_port = None):
        """Thin wrapper for the logClient.getClientLogger method.

        Since the configuration is normally accessed with this class,
        the logger is easily configured using this helper method.
        """
        if log_server_port is None:
            log_server_port = self.parseProjectConfig()["log_server_port"]

        kwargs = {"log_server_port" : log_server_port,
                  "log_server_level" : int(self.get("log_server_level", "Logging")),
                  "log_client_level" : int(self.get("log_client_level", "Logging"))}
        return logClient.getClientLogger(logger_name=logger_name, **kwargs)
    #-----------------------------------------------------------
    def logConfig(self, logger):
        logger.info("Current simulation path: " + self.sim_path)
        logger.info("Configuration file: " + self.config_file)
        sections = self.cfg.sections()
        sections.append("DEFAULT")
        for section in sections:
            items = self.cfg.items(section)
            if len(items) > 0:
                logger.debug("  [" + section + "]")
                for item in items:
                    logger.debug("   " + repr(item[0]) + " = " + repr(item[1]))
        for item in self.unrecognized_options.items():
            logger.warning("Unrecognzied option '" + item[1]
                                + "' in section '" + item[0] + "' found.")
        if len(self.unrecognized_options) > 0:
            logger.warning("Unrecognized options found in the configuration"
                                +", please see the default.cfg for valid options.")

    #-----------------------------------------------------------
    def _parse_config_file(self, default_config, config):
        self.cfg = ConfigParser.SafeConfigParser()
        # Enable case sensitive option keys:
        self.cfg.optionxform = str
        self.cfg.read(default_config)

        custom_cfg = ConfigParser.SafeConfigParser()
        custom_cfg.optionxform = str
        custom_cfg.read(config)

        for section in custom_cfg.sections():
            for item in custom_cfg.items(section):
                if not self.cfg.has_option(section, item[0]):
                    self.unrecognized_options[section]=item[0]
                self.cfg.set(section, item[0], item[1])

        
#-----------------------------------------------------------
def normPath(*paths):
    """Accept one or several paths and returns the joined, normalized, absolute path."""
    return os.path.abspath(os.path.join(*paths))
