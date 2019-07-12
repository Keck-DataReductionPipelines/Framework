'''
Created on Jul 8, 2019

@author: shkwok
'''

from models.action import Action


class Base_instrument:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.event_table0 = {
            'echo':      ('echo', 'stop', None),
            'time_tick': ('echo', None, None),
            }

    def true (self, *args):
        return True
    
    def _get_action (self, prefix, action):        
        name = prefix + action
        try:
            return self.__getattribute__ (name)
        except:
            return self.true
        
    def get_pre_action (self, action):
        return self._get_action ('pre_', action)
    
    def get_post_action (self, action):
        return self._get_action('post_', action)
    
    def get_action (self, action):
        return self._get_action('', action)
    
    def noop (self, arg, context):
        print ("Nothing here", arg)
        
    def echo (self, arg, context):
        print ("echo", arg)
        
    def event_to_action (self, event, context):
        event_info = self.event_table0.get(event.name)
        if not event_info is None:
            return event_info
        return 'noop', None

    
if __name__ == '__main__':
    pass
