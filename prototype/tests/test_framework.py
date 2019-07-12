'''
Created on Jul 8, 2019

@author: shkwok
'''

from core.framework import Framework
from pipelines.test_pipeline import Test_pipeline
from utils.DRPF_logger import DRPF_logger

import time

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    pipeline = Test_pipeline()
    framework = Framework(pipeline)
    
    DRPF_logger.info ("Framwork initialized")
    framework.start()
        
    framework.push_event('event1', 'no arg')
    while not framework.must_stop:
        time.sleep (1)
        
    DRPF_logger.warning ("Terminating")
