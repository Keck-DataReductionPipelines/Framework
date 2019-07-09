'''
Created on Jul 8, 2019

@author: shkwok
'''

import queue

class Action_queue (queue.Queue):
    '''
    classdocs
    '''


    def __init__(self, *args, **kargs):
        '''
        Constructor
        '''
        super(Action_queue, self).__init__(*args, **kargs)
    
class Event_queue (queue.Queue):
    '''
    classdocs
    '''


    def __init__(self, *args, **kargs):
        '''
        Constructor
        '''
        super(Event_queue, self).__init__(*args, **kargs)
            
