'''
Created on Jul 31, 2019

Test CCD basic

@author: skwok
'''

import sys
import os.path
import glob
import threading

from core.framework import Framework

from config.framework_config import ConfigClass
from pipelines.ccd_basic_pipeline import ccd_basic_pipeline
from models.arguments import Arguments

#
# Local functions
#


if __name__ == '__main__':
    
    if len (sys.argv) >= 2:
        path = sys.argv[1]
    
        pipeline = ccd_basic_pipeline()
        framework = Framework(pipeline, "config.cfg")
        framework.config.instrument = ConfigClass ("instr.cfg")
        framework.logger.info ("Framework initialized")
        
        if os.path.isdir(path):
            flist = glob.glob(path + '/*.fits')
            for f in flist:
                args = Arguments(name=f)
                framework.append_event ('next_file', args) 
                
        else:
            framework.logger.info ("Exepected directory")        
        
        framework.start()                
        framework.waitForEver()
    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))        
