"""
    This module defines a set of functions which will take a receiver
    connection and perform a statistical test with it.
"""
import time

def AdvStatsTest(g,n,t,con):
    """
        This test sets the receiver's power level to 'g' and queries the
        receiver 'n' times at a sampling rate of 't' seconds.
        
        The test will return a dictionary whose keys are the IDs of detected
        tags and the keys being the number of times the tag was detected.
    """
    CurrentFrequency = lambda x,y : (x in y and y[x]) or 0
    freq = dict()
    
    con.setGain(g)
    for i in range(n):
        for id in [c['id'] for c in con.getData()]:
            freq[id] = CurrentFrequency(id,freq) + 1        
        time.sleep(t)
        
    return freq

def SimpleStatsTest(n,t,g,id,con):
    """
        This test sets the receiver's power level to 'g' and queries the
        receiver 'n' times at a sampling rate of 't' seconds.
        
        The test will return the number of times that the tag defined by
        'id' is detected.
    """
    CountDetections = lambda x,y : len([ c['id'] for c in y if c['id'] == x ])
    passes = 0
    
    con.setGain(g)
    for i in range(n):
        passes += CountDetections(id, con.getData())
        time.sleep(t)
        
    return passes