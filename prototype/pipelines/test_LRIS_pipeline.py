'''
FITS to PNG Pipeline


This is to demonstrate and test the framework.
For each FITS file in a given directory, a PNG file is produced.

To simulate multiple steps, a simple noise removal median filter and a histogram equalization will applied before the 
actual PNG conversion.  

Created on Jul 15, 2019

@author: lrizzi
'''

from pipelines.base_pipeline import Base_pipeline
from utils.DRPF_logger import DRPF_logger

'''
from primitives.noise_removal import noise_removal
from primitives.hist_equal2d import hist_equal2d
from primitives.simple_fits_reader import simple_fits_reader
from primitives.save_png import save_png
'''

from primitives.create_contact_sheet_HTML import create_contact_sheet_HTML


class test_LRIS_pipeline (Base_pipeline):
    """
    Pipeline to convert FITS to PNG including median noise removal and histogram equalization.
    
    """
    
    event_table = {
    'next_file'     : ('simple_fits_reader', 'file_ready', None),
    }

    def __init__ (self):
        '''
        Constructor
        '''
        Base_pipeline.__init__(self)
        self.cnt = 0        
        

    
if __name__ == '__main__':
    """
    Standalone test
    """
    pass
