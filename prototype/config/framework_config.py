'''
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: shkwok
'''

from models.event import Event
import datetime
from Cython.Shadow import typeof


class ConfigClass:    
    
    def __init__ (self, cgfile=None):
        self.properties = {}
        if not cgfile is None:
            self.read(cgfile)
    
    def getType (self, value):
        value = value.strip()
        try:
            i = int(value)
            return i
        except:
            pass
        
        try:
            f = float(value)
            return f
        except:
            pass
        
        if value == "True":
            return True
        if value == "False":
            return False
        
        try:
            return eval(value)
        except:
            return value
        
    def read (self, fname):        
        with open(fname, 'r') as fh:
            props = self.properties
            for line in fh:
                line = line.strip()
                if len(line) < 1: continue
                try:
                    idx = line.index("#")
                    line = line[:idx]
                except:
                    pass
                if len(line) < 1: continue
                parts = line.split('=')
                if len(parts) > 1:
                    key, val = parts
                    key = key.strip()              
                    props[key] = self.getType (val)
            return
        raise Exception("Failed to read configuration file " + fname)

    def __getattr__ (self, key):
        return self.properties[key]

if __name__ == "__main__":
    Config = ConfigClass ()
    Config.read("config.cfg")
    #print(Config.__dict__)
    
    print (Config.denoise_sigmas[1])
    print (Config.no_event_event)
    