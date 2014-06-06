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
    def __init__(self, config_file, sim_path = None):
        """Initializes this module to use a specific configuration file

        config_file is the path to the configuration file.
        sim_path sets the project directory in which the simulations
        will take place and is generated if None, but not written or
        created in any form.
        """
        
        self.config_file = normPath(config_file)
        self.cfg = ConfigParser.ConfigParser()
        # Enable case sensitive option keys:
        self.cfg.optionxform = str
        self.cfg.read([DEFAULT_CONFIG, self.config_file])

        if sim_path is None:
            self.sim_path = self.generate_output_path()
        else:
            self.sim_path = normPath(sim_path)

    #-----------------------------------------------------------
    def get(self, key, section = "Global"):
        return self.cfg.get(section, key)

    #-----------------------------------------------------------
    def getDefault(self, key, section = "Global", default=None):
        if self.cfg.has_option(section, key):
            return self.cfg.get(section, key)
        return default
    #-----------------------------------------------------------
    def getPath(self, key, section = "Global"):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current working directory,
        not the sim_path. Use getLocalPath() for a variant
        relative to the simulation directory.
        """
        return normPath(self.get(key, section))

    #-----------------------------------------------------------
    def getLocalPath(self, key, section = "Global"):
        """Returns a normalized path specified by the config
        file.

        The absolute base path is the current sim_path for this
        function. Use getPath() for a variant relative to the
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
                        + self.getDefault("result_affix", default="result")
        output_path = normPath(self.getPath("result_directory"),
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
        filename = self.getLocalPath("projectConfig")
        with open(filename, 'r') as config:
            c = 0 #counter
            for line in config:
                line = line.strip()
                c = c+1
                if c == 1:
                    values.update(projName = line)
                elif c == 2:
                    values.update(projPath = line)
                elif c == 3:
                    values.update(simConfig = line)
                elif c == 4:
                    values.update(stimulation = line)
                elif c == 5:
                    values.update(cellname = line)
                elif c == 6:
                    values.update(duration = int(line))
                elif c == 7:
                    values.update(dt = float(line))
                elif c == 8:
                    currents = line.strip("[").strip("]").split(",")
                    values.update(currents = currents)
                    values.update(numCurrents = int(currents[0]))
                    values.update(startCurrent = float(currents[1]))
                    values.update(stepCurrent = float(currents[2]))
                elif c == 9:
                    values.update(mode = line)
        return values
    #-----------------------------------------------------------
    def parseIndexFile(self):
        """Index (idx) der gebrauchten Leitfähigkeiten aus Datei lesen: Wert in der 2. Zeile!"""
        filenameIndex = self.getLocalPath("candidateIndex")
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
    def getClientLogger(self, logger_name):
        """Thin wrapper for the logClient.getClientLogger method.

        Since the configuration is normally accessed with this class,
        the logger is easily configured using this helper method.
        """
        kwargs = {"log_server_port" : int(self.get("log_server_port", "Logging")),
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
                logger.info("  [" + section + "]")
                for item in items:
                    logger.info("   " + repr(item[0]) + " = " + repr(item[1]))
#-----------------------------------------------------------
def normPath(*paths):
    """Accept one or several paths and returns the joined, normalized, absolute path."""
    return os.path.abspath(os.path.join(*paths))
