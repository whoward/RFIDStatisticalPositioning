"""
    This module contains an implementation of the ObservationsManager 
    which is intended to efficiently store a large number of observations.
    
    The Dynamic implementation of this manager essentially stores
    observations in a hash table.  The key of this hash table is as
    always (R,G) where R is the receiver and G is the gain level of
    the receiver.  While not efficient with memory this manager does
    feature the ability to prune its own data strategically, making
    tracking moving objects conceivably possible.  The manner it uses
    to achieve this is simply the sliding window approach.
"""
from __future__ import with_statement
from Thesis.constants import *
import threading, time

class ObservationTable():
    def __init__(self,window):
        self.window = window
        self.table = dict()
        self.locks = dict()
                
        for recv in known_hosts.values():
            for gain in range(32):
                self.table[(recv,gain)] = []
                self.locks[(recv,gain)] = threading.RLock()
    
    def prune(self,ctime):
        expire = ctime - self.window
        
        for recv,gain in self.table.keys():
            key = (recv,gain)
            with self.locks[key]:
                new = [x for x in self.table[key] if x[0] >= expire]
                self.table[key] = new 
        
    def get(self,recv,gain):
        key = (recv,gain)
        
        with self.locks[key]:
            n = len(self.table[key])
            x = len([x for x in self.table[key] if x[1]])
            
        return (n,x)
    
    def update(self,recv,gain,time,detected):
        self.table[(recv,gain)].append( (time,detected) )

class ObservationsManager(threading.Thread):
    def __init__(self,window,prunerate=0.1):
        # Some variables which affect pruning
        self.mostrecent = 0
        self.rate = prunerate
        
        # Create the observation tables for each expected tag
        self.tables = dict()
        for tagid in known_tags.values():
            self.tables[tagid] = ObservationTable(window)
            
        self.observers = []
        self.observationCount = 0

        # Initialize the thread
        threading.Thread.__init__(self)
        
    def put(self,reading):
        recv,gain,detected,ctime = reading
            
        for tag in known_tags.values():
            self.tables[tag].update( recv, gain, ctime, tag in detected )
            
        if ctime > self.mostrecent:
            self.mostrecent = ctime
            
        self.observationCount = self.observationCount + 1
            
        for observer in self.observers:
            observer[2][0] = observer[2][0] - 1
            if observer[2][0] <= 0:
                observer[2][0] = observer[1]
                observer[0].notify(self)
    
    def run(self):
        while True:
            time.sleep(self.rate)
            for tag,table in self.tables.items():
                table.prune(self.mostrecent)
    
    def addUpdateListener(self,object,interval):
        self.observers.append( (object,interval,[interval]) )
    
    def get(self,tag,recv,gain):
        return self.tables[tag].get(recv,gain)