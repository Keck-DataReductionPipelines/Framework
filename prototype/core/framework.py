'''
Created on Jul 8, 2019

@author: skwok
'''

import datetime
import threading
import signal
import traceback
import time

from utils.DRPF_logger import DRPF_logger
from core.queues import Event_queue

from models.processing_context import Processing_context
from models.arguments import Arguments
from models.action import Action
from models.event import Event

from config.framework_config import Config

class Framework(object):
    '''
    This class implements the core of the framework.
    There are two threads: the event loop and the action loop.
    '''
    
    def __init__(self, pipeline):
        '''
        pipeline: a class containing recipes
        
        Creates the event_queue and the action queue
        '''
        self.event_queue = Event_queue()
        self.event_queue_hi = Event_queue()   
        
        self.pipeline = pipeline
        self.context = Processing_context (self.event_queue_hi)
        self.keep_going = True        
        self.init_signal ()
        
    def get_event (self):
        try:
            try:
                return self.event_queue_hi.get_nowait()
            except:                                       
                return self.event_queue.get(True, Config.event_timeout)
        except Exception as e: 
            #args = Arguments(name='tick', time=datetime.datetime.ctime(datetime.datetime.now()))
            #return Event ('time_tick', args)
            return None
        

    def _push_event (self, event_name, args):
        '''
        Pushes high priority events
        
        Normal events go to the lower priority queue
        Only used in execute.
        
        '''
        DRPF_logger.info (f"Push event {event_name}, {args.name}")
        self.event_queue_hi.put(Event (event_name, args))
        
    def append_event (self, event_name, args):
        '''
        Appends low priority event to the end of the queue
        '''                
        self.event_queue.put (Event (event_name, args))
     
                                   
    def event_to_action (self, event, context):
        '''
        Passes event.args to action.args
        
        Note that event.args comes from previous action.output.
        '''
        event_info = self.pipeline.event_to_action (event, context)
        DRPF_logger.info (f'Event to action {event_info}')
        return Action (event_info, args=event.args)
    
    def execute (self, action, context):
        '''
        Executes one action
        The input for the action is in action.args.
        The action returns action_output and it is passed to the next event if action is successful.
        '''
        instr = self.pipeline
        action_name = action.name
        try:
            if instr.get_pre_action(action_name)(action, context):
                if Config.print_trace:
                    DRPF_logger.info ('Executing action ' + action.name)
                action_output = instr.get_action(action_name)(action, context)
                if instr.get_post_action(action_name)(action, context):
                    if not action.new_event is None:
                        self._push_event (action.new_event, action_output)
                    if not action.next_state is None:
                        context.state = action.next_state
                    if Config.print_trace:
                        DRPF_logger.info ('Action ' + action.name + ' done')
                    return
                else:
                    # post-condition failed
                    context.state = 'stop'
            else:
                # Failed pre-condition
                context.state = 'stop'
        except:
            DRPF_logger.error ("Exception while invoking {}. Execution stopped.".format (action_name))
            context.state = 'stop'
            if Config.print_trace:
                traceback.print_exc()
    
    def start_action_loop (self):
        '''
        This is a thread running the action loop.
        '''
        def loop ():
            while self.keep_going:
                try:    
                    action = ''
                    event = ''
                    event = self.get_event ()
                    if event is None:                        
                        DRPF_logger.info ("No new events - do nothing")
                    
                        if self.event_queue.qsize() == 0 and \
                            self.event_queue_hi.qsize() == 0:
                            DRPF_logger.info (f"No pending events or actions, terminating")
                            self.keep_going = False
                    else:       
                        action = self.event_to_action (event, self.context)                        
                        self.execute(action, self.context)
                    if self.context.state == 'stop':
                        break
                except Exception as e:
                    DRPF_logger.error (f"Exception while processing action {action}, {e}")
                    break                
            self.keep_going = False
            
        thr = threading.Thread (name='action_loop', target=loop)
        thr.setDaemon(True)
        thr.start()

    def init_signal (self):
        '''
        Captures keyboard interrupt
        '''
        def handler (*args):
            self.keep_going = False

        # signal.signal (signal.CTRL_BREAK_EVENT, handler)
        signal.signal (signal.SIGINT, handler)
        
    def start (self):
        '''
        Starts the event loop and the action loop
        '''  
        self.start_action_loop ()
        
    def waitForEver (self):            
        while self.keep_going:
            time.sleep (1)
