'''
Created on Jul 8, 2019

@author: shkwok
'''

import sys
import os.path
import glob

from core.framework import Framework

from pipelines.fits2png_pipeline_with_actions import Fits2png_pipeline_with_actions
from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments

from config.framework_config import Config

import time

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    
    if len (sys.argv) >= 2:
        path = sys.argv[1]
    
        pipeline = Fits2png_pipeline_with_actions() 
        framework = Framework(pipeline)
        
        DRPF_logger.info ("Framework initialized")
            
        if os.path.isdir(path):
            flist = glob.glob(path + '/*.fits')
            for f in flist:
                args = Arguments(name=f)
                framework.append_event ('next_file', args)
                    
            
            out_dir = Config.output_directory
            out_name = 'test_w_actions.html'
            framework.append_event ('contact_sheet', 
                Arguments(dir_name=out_dir, pattern='*.png', out_name=out_name, cnt=len(flist)))            
                
        else:        
            args = Arguments(name=path)
            framework.append_event('next_file', args)
        
        framework.start()                
        framework.waitForEver()
    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))        
