"""
    This module contains a DataSource implementation to retrieve simulated
    observations.
"""
from Thesis.constants import known_hosts 
import threading, time, random

class Simulator(threading.Thread):
    """
        The Simulator class quite simply attempts to simulate observations
        being retrieved from a GAO RFID Receiver given a number of parameters.
        
        This class will make use of the constants defined in the
        Thesis.constants module to determine which receiver names should be
        used.
    """
    def __init__(self,queue,cali,tag,movement,mobility):
        """
            Constructs a Simulator instance. 
            
            Simulated observations will be continually offered to the queue 
            'queue'.    
            
            The calibration data used to determine the likelihood of detection
            is passed as the variable 'cali', a key-value mapping is expected.
            The key of the mapping is a tuple of the receiver, the gain, and
            the position.  The value is the probability as a floating point
            number between 0 and 1 inclusive.
            
            The only tag that will be simulated will be identified by the 
            value of 'tag'.
            
            The movement variable is expected to be an array of integers,
            describing the path the tag takes during the simulation.
            
            The mobility variable defines the number of observations between
            steps in the movement array.
        """        
        self.movement = movement
        self.mobility = mobility
        
        self.movepos = 0
        self.countdown = mobility
        
        self.queue = queue        
        self.cdata = cali
        self.pos = self.movement[0]
        self.tag = tag
        
        threading.Thread.__init__(self)
    
    def run(self):
        ctime = time.time()
        
        while True:
            # Go through the expected power levels
            for gain in range(32):
                # Go through every expected receiver
                for recv in known_hosts.values():
                    # find the probability of detecting the tag at the current
                    # position and make a probability test to determine if it
                    # was detected
                    p = self.cdata.get((recv, gain, self.pos))
                    if random.random() < p:
                        observation = (recv, gain, [self.tag], ctime)
                    else:
                        observation = (recv, gain, [], ctime)
                        
                    # if the queue is iterable lets assume its a list of queues and
                    # write the observation to every one of them
                    if not hasattr(self.queue,'__iter__'):
                        self.queue.put(observation)
                    else:
                        for queue in self.queue:
                            queue.put(observation)
                    
                    # Increment the current time by a second
                    ctime += 1.0
                    self.countdown = self.countdown - 1
                    
                    # If it is time to move to the next position do so
                    if self.countdown <= 0:
                        self.countdown = self.mobility
                        self.movepos = (self.movepos + 1) % len(self.movement)
                        self.pos = self.movement[ self.movepos ]
                    