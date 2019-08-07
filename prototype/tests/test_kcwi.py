'''
Created on Jul 19, 2019

Test Fits to PNG pipeline with HTTP server.

@author: skwok
'''

import sys
import os.path
import glob

from core.framework import Framework
from config.framework_config import ConfigClass

from pipelines.kcwi_pipeline import Kcwi_pipeline
from models.arguments import Arguments
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as pl


if __name__ == '__main__':


    if len(sys.argv) >= 2:
        path = sys.argv[1]

        pipeline = Kcwi_pipeline()
        framework = Framework(pipeline, 'config.cfg')
        framework.config.instrument = ConfigClass("instr.cfg")
        framework.logger.info("Framework initialized")

        framework.logger.info("Checking path for files")


        if os.path.isdir(path):
            flist = glob.glob(path + '/*.fits')
            for f in flist:
                args = Arguments(name=f)
                framework.append_event('next_file', args)

        else:
            args = Arguments(name=path)
            framework.append_event('next_file', args)

        framework.start()
        framework.waitForEver()
    else:
        print ("Usage {} dir_or_file".format(sys.argv[0]))