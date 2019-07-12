'''
Created on Jul 8, 2019

This is the base pipeline.

@author: skwok
'''

import sys
import importlib
from utils.DRPF_logger import DRPF_logger

class Base_pipeline:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.event_table0 = {
            'noop':     ('noop', None, None),        
            'echo':      ('echo', 'stop', None),
            'time_tick': ('echo', None, None),
            }

    def true (self, *args):
        return True
    
    def _get_action_apply_method (self, klass):
        def f (action, context):
            obj = klass (action, context)
            return obj.apply()
        return f
        
    
    def _find_import_action (self, module_name):   
        full_name = 'primitives.' + module_name.lower()        
        mod = importlib.import_module(full_name)        
        return self._get_action_apply_method(getattr (mod, module_name))        
           
    
    def _get_action (self, prefix, action):  
        '''
        Returns a function for the given action name or true() if not found
        '''      
        name = prefix + action
        try:
            return self.__getattribute__ (name)            
        except:
            try:
                return self._find_import_action (name)
            except:
                return self.true
        
    def get_pre_action (self, action):
        return self._get_action ('pre_', action)
    
    def get_post_action (self, action):
        return self._get_action('post_', action)
    
    def get_action (self, action):
        return self._get_action('', action)
    
    def noop (self, action, context):
        DRPF_logger.info (f"NOOP action {action}")
    
    def no_more_action (self, ation, context):
        DRPF_logger.info ("No more action, terminating")
        
    def echo (self, action, context):
        DRPF_logger.info  (f"Echo action {action}")
        
    def _event_to_action (self, event, context):
        '''
        Returns the event_info as (action, state, next_event)
        '''
        noop_event = self.event_table0.get('noop')
        event_info = self.event_table0.get(event.name, noop_event)
        return event_info
    
    def event_to_action (self, event, context):
        event_info = self.event_table.get(event.name)
        if not event_info is None:
            return event_info
        return self._event_to_action(event, context)

