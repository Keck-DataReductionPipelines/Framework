'''
Created on Jul 8, 2019

@author: shkwok
'''

from core.framework import Framework

from pipelines.fits2png_pipeline_with_actions import Fits2png_pipeline_with_actions
from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments

import time

def new_file (name):
    pass
    

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    
    pipeline = Fits2png_pipeline_with_actions()
    framework = Framework(pipeline)
    
    DRPF_logger.info ("Framework initialized")
    framework.start()
    
    args = Arguments()
    args.name = '../../test_fits/nirspecm000_0022.fits'
    
    framework.emit_event('next_file', args)
    while not framework.must_stop:
        time.sleep (1)
        
    DRPF_logger.warning ("Terminating")
