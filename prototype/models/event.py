'''
Created on Jul 8, 2019

@author: shkwok
'''

class Event(object):
    '''
    classdocs
    '''


    def __init__(self, name, args):
        '''
        Constructor
        '''
        self.name = name
        self.args = args
        
    def __lt__ (self, a):
        return self.name < a.name
    
    
    def __str__ (self):
        return f"Event {self.name}, args={self.args}"
