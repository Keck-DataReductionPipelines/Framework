'''
Created on Jul 8, 2019

@author: shkwok
'''

import time
from models.base_instrument import Base_instrument

class Test_instrument(Base_instrument):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        Base_instrument.__init__(self)
        self.init_event_table()
        
    def init_event_table (self):
        table = {
            'event1': ('action1', 'running', 'event2'),
            'event2': ('action2', 'running', 'event3'),
            'event3': ('action3', 'stop', None),
            }
        self.event_table = table

    def action1 (self, arg, contenxt):
        print ("Action 1")
        time.sleep(3)
        
    def action2 (self, arg, contenxt):
        print ("Action 2")
        time.sleep (10)
        
    def action3 (self, arg, context):
        print ("Action 3")
        time.sleep (2)
        
    def pre_action3 (self, arg, context):
        print ("Pre action 3")
        return True
    
    def event_to_action (self, event, context):
        event_info = self.event_table.get(event.name)
        if event_info:
            return event_info
        return Base_instrument.event_to_action(self, event, context)
