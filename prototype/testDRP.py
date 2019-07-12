'''
Created on Jul 8, 2019

@author: shkwok
'''

from core.framework import Framework
from test_instrument import Test_instrument
import time

if __name__ == '__main__':
    instrument = Test_instrument()
    framework = Framework(instrument)
    framework.start()
        
    framework.context.emit_event('event1', 'no arg')
    while not framework.must_stop:
        time.sleep (1)
        
    print ("Terminated")
