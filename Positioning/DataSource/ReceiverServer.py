"""
    This module contains a DataSource implementation to handle parsing data from
    an Observation Dump File.
"""
from Protocol.GAORfidReceiver import Server
import threading, time

class ReceiverConnection(threading.Thread):
    """
        The ReceiverConnection class takes a RFID receiver connection and 
        continually sweeps up from the minimum gain level (0) to the maximum
        gain level (31).  At each gain level the receiver will be queried
        'n' times with 't' seconds between each query.  Data collected will
        be offered to the queue 'queue' and then immediately forgotten.        
    """
    def __init__(self,driver,queue,t,n):
        self.driver = driver
        self.queue = queue
        
        self.rate = t
        self.number = n
        
        threading.Thread.__init__(self)
        
    def run(self):
        
        while True:
            for gain in range(32):
                self.driver.setGain(gain)
                
                for i in range(self.number):
                    taglist = []
                    for detected in self.driver.getData():
                        taglist.append( detected['id'] )
                    observation = (self.driver.addr,gain,taglist,time.time())
                    
                    # if the queue is iterable lets assume its a list of queues and
                    # write the observation to every one of them
                    if not hasattr(self.queue,'__iter__'):
                        self.queue.put(observation)
                    else:
                        for queue in self.queue:
                            queue.put(observation)
                    
                    time.sleep(self.rate)
        
class ReceiverServer(threading.Thread):
    """
        The ReceiverServer class makes use of the GAORfidReceiver protocol
        classes to continually accept connections from RFID Receivers and then
        delegate handling of those connections to another thread which will
        handle parsing and offering data to the queue.
    """
    def __init__(self,queue,t,n):
        """
            Constructs a server which will continually accept connections.
            When a connection is received the RFID receiver will be initially
            configured to query at a rate of 't' seconds and take 'n' samples
            per gain level.  See ReceiverConnection class for details.
            
            For each observation made the observation will be offered to the
            queue 'queue'. 
        """
        self.server = Server()
        self.server.connect()
        
        self.queue = queue
        self.rate = t
        self.count = n
        
        threading.Thread.__init__(self)
    
    def run(self):
        
        while True:
            drv = self.server.getNextConnection()

            thread = ReceiverConnection(driver=drv,queue=self.queue,t=self.rate,n=self.count)
            thread.start()