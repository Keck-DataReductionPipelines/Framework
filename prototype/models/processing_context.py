'''
Created on Jul 8, 2019

@author: shkwok
'''

from models.event import Event


class Processing_context:
    '''
    classdocs
    '''

    def __init__(self, event_queue):
        '''
        Constructor
        '''
        self.name = 'Processing_context'
        self.state = 'Undefined'
        self.event_queue = event_queue
        
    def emit_event (self, name, arg):
        self.event_queue.put_nowait(Event (name, arg))
