'''
Created on Jul 8, 2019

@author: shkwok
'''

import os
import threading
import time
import glob

from utils import framework_config


class Data_set:
    '''
    classdocs
    '''

    def __init__(self, dirname):
        '''
        Constructor
        '''
        self.dir_name = dirname
        self.data_table = {}
        self.must_stop = False
        self.monitor_interval = framework_config.Config.monitor_interval
        self.file_type = framework_config.Config.file_type
        self.update_date_set()
    
    def digest_new_item (self, name):
        return os.stat(name)
        
    def update_date_set (self):

        def digest (long_name):
            fname = os.path.basename(long_name)
            item = self.data_table.get(fname)
            if item is None:
                self.data_table[fname] = self.digest_new_item (long_name)
                print ("got", fname)
            
        flist = glob.glob (self.dir_name + '/' + self.file_type)
        for f in flist:
            digest (f)
        
    def loop (self):
        '''
        Waits for changes in the directory, then digests the changes.
        Maybe needs to monitor other events also
        '''
        ok = True
        last_time = 0
        while ok:
            dir_state = os.stat(self.dir_name)
            curr_time = dir_state.st_mtime
            if curr_time > last_time:
                self.update_date_set ()
                last_time = curr_time
            time.sleep (self.monitor_interval)
            if self.must_stop:
                break
            
    def start_monitor (self):
        '''
        Monitors for changes in the given directory
        '''
        thr = threading.Thread(target=self.loop)
        thr.setDaemon(True)
        thr.start()
        
    def stop_monitor (self):
        self.must_stop = True

        
if __name__ == '__main__':
    data_set = Data_set ('.')
    data_set.start_monitor()
    time.sleep (50)
    data_set.stop_monitor()
    print (data_set.data_table)
