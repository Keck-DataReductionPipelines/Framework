'''
FITS to PNG Pipeline


This is to demonstrate and test the framework.
For each FITS file in a given directory, a PNG file is produced.

To simulate multiple steps, a simple noise removal median filter and a histogram equalization will applied before the 
actual PNG conversion.  

Created on Jul 8, 2019

@author: shkwok
'''

from pipelines.base_pipeline import Base_pipeline
from primitives.noise_removal import noise_removal
from primitives.hist_equal2d import hist_equal2d
from primitives.simple_fits_reader import simple_fits_reader
from primitives.save_png import save_png


class Fits2png_pipeline_with_actions (Base_pipeline):
    """
    Pipeline to convert FITS to PNG including median noise removal and histogram equalization.
    
    """
    
    event_table = {
    'next_file'     : ('read_file', 'file_ready', 'file_ready'),
    'file_ready'    : ('remove_noise', 'noise_removed', 'noise_removed'),
    'noise_removed' : ('hist_eq_alternative', 'histeq_done', 'histeq_done'),    
    'histeq_done'   : ('save_png', 'idle', None)
    }

    def __init__ (self):
        '''
        Constructor
        '''
        Base_pipeline.__init__(self)        
    
    def read_file (self, action, context):
        fr = simple_fits_reader (action, context)
        return fr.apply()
        
    def remove_noise (self, action, context):
        nr = noise_removal (action, context)
        return nr.apply()
    
    def hist_eq_alternative (self, action, context):
        hq = hist_equal2d(action, context)
        return hq.apply()
    
    def save_png (self, action, context):
        sp = save_png(action, context)
        action.args.out_name = ''
        return sp.apply ()

    
if __name__ == '__main__':
    """
    Standalone test
    """
    pass
