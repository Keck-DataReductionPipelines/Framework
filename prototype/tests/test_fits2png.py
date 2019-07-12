'''
Created on Jul 8, 2019

@author: shkwok
'''

import sys
import os.path
import glob

from core.framework import Framework

from pipelines.fits2png_pipeline import Fits2png_pipeline
from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments

import time

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    
    if len (sys.argv) >= 2:
        path = sys.argv[1]
    
        pipeline = Fits2png_pipeline() 
        framework = Framework(pipeline)
        
        DRPF_logger.info ("Framework initialized")
            
        if os.path.isdir(path):
            flist = glob.glob(path + '/*.fits')
            for f in flist:
                args = Arguments()
                args.name = f
                print (f)
                framework.append_event ('next_file', args)
        else:        
            args = Arguments()
            args.name = path    
            framework.push_event('next_file', args)
        
        framework.start()        
        framework.waitForEver()
    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))        
