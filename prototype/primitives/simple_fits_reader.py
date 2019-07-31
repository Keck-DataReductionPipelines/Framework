'''
Created on Jul 9, 2019
                
@author: skwok
'''

import astropy.io.fits as pf 
from astropy.utils.exceptions import AstropyWarning
import warnings

from models.arguments import Arguments
from primitives.base_primitive import Base_primitive


class simple_fits_reader (Base_primitive):
    '''
    classdocs
    '''

    def __init__(self, action, context):
        '''
        Constructor
        '''    
        Base_primitive.__init__(self, action, context)
        
    def open (self, name):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', AstropyWarning)
            return pf.open(name)

    def _perform (self):
        '''
        Expects action.args.name as fits file name
        Returns HDUs or (later) data model
        '''
        name = self.action.args.name
        self.logger.info (f"Reading {name}")
        out_args = Arguments()
        out_args.name = name
        out_args.hdus = self.open(name)
        
        return out_args
    
         
           