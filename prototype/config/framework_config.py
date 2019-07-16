'''
Created on Jul 8, 2019

This is a simple collection configuration parameters.

To do: 
    import configuration from primitives or recipes. 
    Read parameters from file.
    

@author: shkwok
'''

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
    
    # end of config
    