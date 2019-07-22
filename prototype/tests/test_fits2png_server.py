'''
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
'''

import sys
import os.path
import glob
import threading

from core.framework import Framework

from pipelines.fits2png_pipeline import Fits2png_pipeline
from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments
from config.framework_config import Config

import time
from tests import test_framework

#
# Local functions
#


if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    
    if len (sys.argv) >= 2:
        path = sys.argv[1]
    
        pipeline = Fits2png_pipeline() 
        framework = Framework(pipeline) 
               
        DRPF_logger.info ("Framework initialized")
        
        DRPF_logger.info ("HTTP server started")
        framework.start_http_server()
            
        if os.path.isdir(path):
            flist = glob.glob(path + '/*.fits')
            for f in flist:
                args = Arguments(name=f)
                framework.append_event ('next_file', args)
                    
            
            out_dir = Config.output_directory
            framework.append_event ('contact_sheet', 
                Arguments(dir_name=out_dir, pattern='*.png', out_name='test.html', cnt=len(flist)))            
                
        else:        
            args = Arguments(name=path)
            framework.append_event('next_file', args)
        
        framework.start()                
        framework.waitForEver()
    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))        
