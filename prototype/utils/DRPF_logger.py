'''
Created on Jul 9, 2019

@author: shkwok
'''

import logging
import logging.config

class DRPF_Logger (logging.getLoggerClass()):
    pass

def getLogger (conf_file=None, name="DRPF"):    
    if not conf_file is None:
        logging.config.fileConfig(conf_file)
    return logging.getLogger(name)