'''
Created on Jul 8, 2019

@author: shkwok
'''

import datetime
import threading
from utils.queues import Action_queue, Event_queue
from models.processing_context import Processing_context
from models.action import Action
from models.event import Event
import signal


class Framework(object):
    '''
    classdocs
    '''
    
    def __init__(self, instrument):
        '''
        instrument: a class containting recipes
        '''
        self.event_queue = Event_queue(5)
        self.action_queue = Action_queue(5)
        self.instrument = instrument
        self.context = Processing_context (self.event_queue)
        self.must_stop = False
        
    def get_event (self):
        try:
            return self.event_queue.get (True, 5)
        except:
            now = datetime.datetime.ctime(datetime.datetime.now())
            return Event ('time_tick', now)
        
    def get_action (self):
        try:
            return self.action_queue.get (True, 3)
        except:
            return Action (('noop', None, None), "No action")
    
    def push_action (self, action):
        print ("push", action)
        self.action_queue.put_nowait(action)
                                
    def event_to_action (self, event, context):
        event_info = self.instrument.event_to_action (event, context)
        return Action (event_info, arg=event.arg)
    
    def start_event_loop (self):
        def loop ():
            ok = True
            context = self.context
            while ok:
                event = self.get_event ()
                action = self.event_to_action (event, context)
                self.push_action (action)
                
        thr = threading.Thread(name='event_loop', target=loop)
        thr.setDaemon(True)
        thr.start()
        
    def execute (self, action, context):
        instr = self.instrument
        action_name = action.name
        arg = action.arg
        if instr.get_pre_action(action_name)(action, context):
            instr.get_action(action_name)(action, context)
            if instr.get_post_action(action_name)(action, context):
                if not action.new_event is None:
                    context.emit_event(action.new_event, action.output)
                if not action.next_state is None:
                    context.state = action.next_state
                return
            else:
                # post-condition failed
                context.state = 'stop'
        else:
            # Failed pre-condition
            context.state = 'stop'
    
    def start_action_loop (self):
        def loop ():
            context = self.context
            while not self.must_stop:
                action = self.get_action ()
                self.execute(action, context)
                if context.state == 'stop':
                    break
            
            self.must_stop = True
        thr = threading.Thread (name='action_loop', target=loop)
        thr.setDaemon(True)
        thr.start()

    def init_signal (self):

        def handler ():
            self.must_stop = True

        # signal.signal (signal.CTRL_BREAK_EVENT, handler)
        signal.signal (signal.SIGINT, handler)
        
    def start (self):
        self.init_signal ()
        self.start_event_loop ()
        self.start_action_loop ()

if __name__ == '__main__':
    t = Framework()
    t.start ()
