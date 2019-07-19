'''
Created on Jul 8, 2019

@author: lrizzi
'''

import sys
import os.path
import glob
import threading

from core.framework import Framework

from utils.DRPF_logger import DRPF_logger
from models.arguments import Arguments
from pipelines.test_LRIS_pipeline import test_LRIS_pipeline


import time

if __name__ == '__main__':
    DRPF_logger.info ("Starting test")


    if len (sys.argv) >= 2:
        path = sys.argv[1]
    
        pipeline = test_LRIS_pipeline()
        framework = Framework(pipeline)

        DRPF_logger.info ("Framework initialized")

        def infinite_loop():
            # then start monitoring for new files
            input_files_before=[]
            while True:
                 DRPF_logger.info("Monitoring...")
                 input_files_now = glob.glob(path + '/*.fits')
                 new_files = [f for f in input_files_now if f not in input_files_before]
                 if len(new_files)>0:
                     print("Processed files: "+str(input_files_before))
                     print("New files: "+str(new_files))
                     for f in new_files:
                         DRPF_logger.info("New file found...:"+f)
                         args = Arguments(name=f)
                         framework.append_event('next_file', args)
                         input_files_before.append(f)
                 time.sleep(5)

        x = threading.Thread(target=infinite_loop)
        x.start()

        framework.start()
        DRPF_logger.info ("Framework started")
        framework.waitForEver()


    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))        
