'''
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: shkwok
'''

from models.event import Event
import datetime

class Config:
    
    name = 'DRP-Framework'
    monitor_interval = 10 # sec
    file_type = '*' # or '*.fits'
    
    print_trace = True
    
    denoise_sigmas = (1, 3)
    denoise_sizes = (3, 3)
    
    push_retries = 5
    event_timeout = 1
    action_timeout = 1
    
    hist_equal_cut_width = 3
    hist_equal_length = 256 * 256
    
    logger_config_file = "../config/logger.conf"

    output_directory = "output"
    
    # What happens when there are no more events ?
    # If no_event_event is None then framework event loop will stop 
    no_event_event = Event ('time_tick', None)
    no_event_wait_time = 5 # sec
    
    # HTTP
    http_server_port = 50100
    doc_root = "."
    
    # end of config
    