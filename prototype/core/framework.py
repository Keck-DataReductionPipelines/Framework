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
from core.queues import Action_queue, Event_queue

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
        self.action_queue = Action_queue(5)
        self.pipeline = pipeline
        self.context = Processing_context (self.event_queue)
        self.keep_going = True        
        self.init_signal ()
        
    def get_event (self):
        try:            
            return self.event_queue.get(True, Config.event_timeout)[1]
        except Exception as e:            
            time.sleep (5)
            args = Arguments(name='tick', time=datetime.datetime.ctime(datetime.datetime.now()))
            return Event ('time_tick', args)
        
    def get_action (self):
        try:
            return self.action_queue.get(True, Config.action_timeout)
        except:
            return None        
    
    def push_action (self, action):
        cnt = Config.push_retries
        while cnt > 0:
            try:
                print ("Action queue size", self.action_queue.qsize())
                self.action_queue.put(action)
                print ("Pushed")
                return
            except:
                traceback.print_exc()
                DRPF_logger.warning ("Action queue full, pausing for 5s before re-trying")
                time.sleep (5)
            cnt = cnt - 1
        DRPF_logging.warning ("Failed to push to action queue after {} tries".format(Config.push_retries))    
        
    def push_event (self, event, args):
        '''
        Pushes high priority events
        '''
        #DRPF_logger.info (f"Push event {event}, {args}")
        self.event_queue.put((1, Event (event, args)))
        
    def append_event (self, event, args):
        '''
        Appends low priority event to the end of the queue
        '''
        self.event_queue.put ((999, Event (event, args)))
                                
    def event_to_action (self, event, context):
        '''
        Passes event.args to action.args
        
        Note that event.args comes from previous action.output.
        '''
        event_info = self.pipeline.event_to_action (event, context)
        return Action (event_info, args=event.args)
    
    def start_event_loop (self):
        '''
        This is a thread running the event loop.
        '''
        def loop ():
            while self.keep_going:
                try:
                    event = ''
                    event = self.get_event ()
                    if event is None:                        
                        DRPF_logger.info ("No new events - do nothing")
                        continue
                        
                    action = self.event_to_action (event, self.context)
                    self.push_action (action)
                except Exception as e:
                    traceback.print_exc()
                    DRPF_logger.error (f'Exception while processing event {event}, {e}')
                    break
                
            self.keep_going = False
                    
                
        thr = threading.Thread(name='event_loop', target=loop)
        thr.setDaemon(True)
        thr.start()
        
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
                    DRPF_logger.info ('Action ' + action.name)
                action_output = instr.get_action(action_name)(action, context)
                if instr.get_post_action(action_name)(action, context):
                    if not action.new_event is None:
                        self.push_event (action.new_event, action_output)
                    if not action.next_state is None:
                        context.state = action.next_state
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
                    acction = ''
                    action = self.get_action ()
                    if action is None:
                        if self.event_queue.qsize() == 0:
                            DRPF_logger.info (f"No more event or actions, terminating")
                            self.keep_going = False
                            
                        continue
                        
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
        def handler ():
            self.keep_going = False

        # signal.signal (signal.CTRL_BREAK_EVENT, handler)
        signal.signal (signal.SIGINT, handler)
        
    def start (self):
        '''
        Starts the event loop and the action loop
        '''
        self.start_event_loop ()        
        self.start_action_loop ()
        
    def waitForEver (self):            
        while self.keep_going:
            time.sleep (1)
