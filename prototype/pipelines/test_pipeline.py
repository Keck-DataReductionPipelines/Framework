'''
Created on Jul 8, 2019

This is a simple sanity test.

@author: shkwok
'''

import time


from utils.DRPF_logger import DRPF_logger

from pipelines.base_pipeline import Base_pipeline

from core.framework import Framework

class Test_pipeline(Base_pipeline):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        Base_pipeline.__init__(self)
        self.init_event_table()
        
    def init_event_table (self):
        table = {
            'event1': ('action1', 'running', 'event2'),
            'event2': ('action2', 'running', 'event3'),
            'event3': ('action3', 'stop', None),
            }
        self.event_table = table

    def action1 (self, action, contenxt):
        DRPF_logger.info ("Action 1 - sleep 3")
        time.sleep(3)
        DRPF_logger.info ("Action 1 - done")
        return 1
        
    def action2 (self, action, contenxt):
        DRPF_logger.info ("Action 2 - sleep 10")
        time.sleep (10)
        DRPF_logger.info ("Action 2 - done")
        return 2
        
    def action3 (self, action, context):
        DRPF_logger.info ("Action 3 - sleep 2")
        time.sleep (2)
        DRPF_logger.info ("Action 3 - done")
        return 3
        
    def pre_action3 (self, action, context):
        DRPF_logger.info ("Pre action 3")
        return True
    
    def event_to_action (self, event, context):
        event_info = self.event_table.get(event.name)
        if event_info:
            return event_info
        return Base_pipeline.event_to_action(self, event, context)


if __name__ == '__main__':
    DRPF_logger.info ("Starting test")
    
    pipeline = Test_pipeline()
    framework = Framework(pipeline)
    
    DRPF_logger.info ("Framwork initialized")
    framework.start()
        
    framework.context.emit_event('event1', 'no arg')
    while not framework.must_stop:
        time.sleep (1)
        
    DRPF_logger.warning ("Terminating")
