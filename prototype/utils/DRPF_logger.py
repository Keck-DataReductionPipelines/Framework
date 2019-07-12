'''
Created on Jul 9, 2019

@author: shkwok
'''

import logging
import logging.config

from config.framework_config import Config

logging.config.fileConfig(Config.logger_config_file)
DRPF_logger = logging.getLogger('DRPF')

