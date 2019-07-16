'''
FITS to PNG Pipeline


This is to demonstrate and test the framework.
For each FITS file in a given directory, a PNG file is produced.

To simulate multiple steps, a simple noise removal median filter and a histogram equalization will applied before the 
actual PNG conversion.  

Created on Jul 8, 2019

@author: shkwok
'''

from pipelines.fits2png_pipeline import Fits2png_pipeline
from primitives.noise_removal import noise_removal as _noise_removal
from primitives.hist_equal2d import hist_equal2d as _hist_equal2d
from primitives.simple_fits_reader import simple_fits_reader
from primitives.save_png import save_png


class Fits2png_pipeline_with_actions (Fits2png_pipeline):
    """
    Pipeline to convert FITS to PNG including median noise removal and histogram equalization.
    
    """
    def __init__ (self):
        '''
        Constructor
        '''
        Fits2png_pipeline.__init__(self)        
    
    def noise_removal (self, action, context):
        nr = _noise_removal (action, context)
        nr.sigmas = (1,1)
        nr.sizes = (3, 3)
        return nr.apply()
    
    def hist_equal2d (self, action, context):
        hq = _hist_equal2d(action, context)
        hq.cut_width = 1.5
        return hq.apply()
    
    
if __name__ == '__main__':
    """
    Standalone test
    """
    pass
