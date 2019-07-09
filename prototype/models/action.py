'''
Created on Jul 8, 2019

@author: shkwok
'''

class Action(object):
    '''
    classdocs
    '''


    def __init__(self, event_info, arg):
        '''
        Constructor
        '''
        self.name, self.next_state, self.new_event = event_info
        self.arg = arg
        self.output = None
        
    def __str__ (self):
        return f"{self.name}, {self.arg}, {self.next_state}, {self.new_event}"
        
