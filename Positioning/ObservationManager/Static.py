"""
    This module contains an implementation of the ObservationsManager 
    which is intended to efficiently store a large number of observations.
    
    The Static implementation of this manager makes use of a frequency
    table to store a great deal of observations very efficiently.  Thread
    pools are even implemented to speed up the process, though the actual
    improvement is not known.  The drawback to using this approach is 
    that once observations are stored there is no efficient way to 
    remove them.
"""
from __future__ import with_statement
from Thesis.constants import known_hosts, known_tags
from Queue import Queue
import threading

class ObservationsTable(object):
    def __init__(self,receivers,gains):
        # Create the table and the individual locks for the rows
        self.table = dict()
        self.rowlocks = dict()
        
        # For printing keep track of the max width of each column entry            
        self.maxrecv = 8
        
        # initialize the values in the table to increase the efficiency of the set methods        
        for recv in receivers:
            self.maxrecv = max(self.maxrecv, len(recv))
            for gain in gains:
                key = (recv,gain)
                self.table[key]    = [0,0]
                self.rowlocks[key] = threading.RLock()
                
    def __str__(self):        
        def hr(): return "+" + "-"*(self.maxrecv+2) + "+" + "-"*6 + ("+" + "-"*7)*2 + "+\n"
        
        strval = hr() + "| Receiver"+" "*(self.maxrecv-8)+" | Gain | Total | Count |\n" + hr()
        
        for key in self.table.keys():
            value = self.get(key)
            strval += "| %s |  %02d  | %05d | %05d |\n" % (key[0],key[1],value[0],value[1])
        
        strval += hr()
        return strval
            
    def detectionEvent(self,key):
        with self.rowlocks[key]:
            self.table[key][0] += 1
            self.table[key][1] += 1

    def nondetectionEvent(self,key):
        with self.rowlocks[key]:
            self.table[key][0] += 1
        
    def get(self,key):
        with self.rowlocks[key]:
            result = self.table[key]
        
        return result
    
class WorkerThread(threading.Thread):
    def __init__(self,manager):
        self.manager = manager
        self.workload = None
        threading.Thread.__init__(self)
    
    def run(self):
        # If there is no workload, nothing can be done
        if self.workload is None:
            return
        
        key = ( self.workload[0], self.workload[1] )
        notdetected = []
        detected = []
        
        # Go through the expected tags, seeing if they are in the detected ones or not
        for tagid in self.manager.taglist:
            if tagid in self.workload[2]:
                detected.append(tagid)
            else:
                notdetected.append(tagid)  
                
        # Call the detection or nondetection event methods
        for tag in detected:
            self.manager.tables[tag].detectionEvent(key)
        for tag in notdetected:
            self.manager.tables[tag].nondetectionEvent(key)       
        
        # Notify the manager of our completion
        self.manager.notify(self)
    
class ObservationsManager(threading.Thread):
    """
        The ObservationsManager class works to optimize memory usage for
        observations.  It does this by maintaining a set of tables for
        each tag which are essentially dictionary objects whose keys are a
        tuple of the Receiver (R) the tag was detected by and the Gain (G) 
        level it was detected at.  The value of the tables is the number of
        detections at (R,G) and the total queries at (R,G) 
    """
    def __init__(self,RecvList=known_hosts.values(),TagList=known_tags.values(),PoolSize=10):
        # Create the worker queue
        self.workqueue = Queue()
        
        # Create the Thread Pool
        self.workpool = Queue(PoolSize)
        for i in range(PoolSize):
            thread = WorkerThread(self)
            thread.start()
            self.workpool.put( thread )
        
        # Create the observation tables for each expected tag
        self.tables = dict()
        for tagid in TagList:
            self.tables[tagid] = ObservationsTable(gains=range(32),receivers=RecvList)
            
        # Save off the tag and receiver list for later usage
        self.recvlist = RecvList
        self.taglist = TagList
        
        # A counter variable
        self.observationCount = 0
        
        # A set of callbacks to call after a number of new observations
        self.callbacks = []
        self.notifylock = threading.RLock()
        
        # Initialize the thread        
        threading.Thread.__init__(self)
    
    def put(self,reading):
        if reading[0] in self.recvlist:
            self.workqueue.put( reading )
    
    def get(self,tag,recv,gain):
        return self.tables[tag].get((recv,gain))
    
    def run(self):
        while True:
            # Block until the next workload is submitted
            work = self.workqueue.get(block=True, timeout=None)
            
            # Get the next available worker thread
            worker = self.workpool.get(block=True, timeout=None)

            # Dispatch the workload
            worker.workload = work
            worker.run()
            
    def addUpdateListener(self,object,interval):
        with self.notifylock:
            self.callbacks.append((object,interval,[interval]))
        
    def notify(self,worker):
        with self.notifylock:
            self.observationCount = self.observationCount + 1
            for i in self.callbacks:
                i[2][0] = i[2][0] - 1
                if i[2][0] <= 0:
                    i[2][0] = i[1]
                    i[0].notify(self)
        self.workpool.put(worker)