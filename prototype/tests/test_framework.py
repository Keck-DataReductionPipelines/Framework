'''
Created on Jul 8, 2019

@author: skwok
'''

from core.framework import Framework
from pipelines.test_pipeline import Test_pipeline
from models.arguments import Arguments

import time

if __name__ == '__main__':
    pipeline = Test_pipeline()
    framework = Framework(pipeline, "config.cfg")
    
    framework.logger.info ("Framwork initialized")
    framework.start()
        
    framework.append_event('event1', Arguments())

    framework.waitForEver()
        
    framework.logger.warning ("Terminating")
