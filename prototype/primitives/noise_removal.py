'''
Created on Jul 8, 2019

@author: skwok
'''

import numpy as np
from models.arguments import Arguments
from primitives.base_primitive import Base_primitive
from config.framework_config import Config
from utils.DRPF_logger import DRPF_logger

class noise_removal (Base_primitive):
    '''
    classdocs
    '''


    def __init__(self, action, context):
        '''
        Constructor
        '''
        Base_primitive.__init__(self, action, context)        
        self.sigmas, self.sizes = Config.denoise_sigmas, Config.denoise_sizes
        
    def _denoise (self, _img, size=3, sigmas=3):
        """
        Finds mean and std.
        For pixels outside mean +/- std *3, finds median and replace pixel
        Returns new image
        """
        def f (x, y):
            x = max(min(w, x), 0)
            y = max(min(h, y), 0)
            return medf(_img[y:y+size,x:x+size])
        
        medf = np.median
        h, w = _img.shape
        mean0 = np.mean (_img)
        std0 = np.std(_img) 
        std1 = std0 * sigmas
        #print ("mean", mean0- std1, mean0+std1)
        idc = np.vstack((np.argwhere(_img > (mean0+std1)), np.argwhere(_img < (mean0-std1))))
        out = np.copy(_img)
        half = size//2
        for a,b in idc:
            out[a,b] = f(b-half,a-half)
        return out
            
    def _perform (self):
        sigmas, sizes = self.sigmas, self.sizes
        args = self.action.args
        DRPF_logger.info (f"noise removal args {args}")        
        hdus = args.hdus
        
        img = hdus[0].data
        for a, b in zip (sizes, sigmas):
            img = self._denoise (img)
            
        out_args = Arguments(name=args.name, img=img)
        return out_args
        
    