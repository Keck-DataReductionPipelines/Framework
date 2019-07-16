'''
Created on Jul 8, 2019

@author: skwok
'''

from core.framework import Framework
from pipelines.test_pipeline import Test_pipeline
from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments

import time

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    pipeline = Test_pipeline()
    framework = Framework(pipeline)
    
    DRPF_logger.info ("Framwork initialized")
    framework.start()
        
    framework.append_event('event1', Arguments())

    framework.waitForEver()
        
    DRPF_logger.warning ("Terminating")
