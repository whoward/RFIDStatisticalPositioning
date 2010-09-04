"""
    This module contains the InferenceEngine class which is intended
    to take a set of calibration data and an observation manager. With
    both of these the InferenceEngine can infer the likelihood of a
    tag existing at all positions defined in the Thesis.constants
    module. 
"""
from Thesis.constants import known_hosts, room_positions
from math import log

def logbinomial(x, n, p):
    """
        This function is used to infer the likelihood of a single 
        position.  It is simply an implementation of the base 10
        logarithm of the binomial function. 
    """
    if x == 0 or p == 0:
        return 0
    try:
        logfac = lambda k: sum(log(x) for x in range(1,k+1))
        return logfac(n) - logfac(x) - logfac(n-x) + x*log(p) + (n-x)*log(1.0-p)
    except:
        raise Exception("logbinominal(%d, %d, %f) error" % (x, n, p))

class InferenceEngine():
    """
        The InferenceEngine class takes an ObservationManager and a set
        of calibration data.  The InferenceEngine's infer method will 
        query the ObservationManager and use the probability defined in
        the calibration data to infer the likelihood of every position.
    """
    
    def __init__(self,ObservationManager,CaliData):
        """
            Constructs an InferenceEngine instance.
            
            The ObservationManager should be an instance of one of the
            observation manager classes defined in the 
            Positioning.ObservationManager module.
            
            The CaliData should be a dictionary representing the calibration 
            data.  The key of this dictionary should be a tuple of the form 
            (R,G,P) where R is the receiver, G is the gain level and P is the
            position.  The value of this dictionary should be the probability
            of detection at the Key.
        """
        self.obsman = ObservationManager
        self.cdata = CaliData

    def infer(self,tag):
        """
            Infers the likelihood of a tag existing at every location defined
            in the room_positions variable from the Thesis.constants module.
            
            Tag is the ID number of the tag to be inferred.
            
            Returns a dictionary whose keys are the positions defined in the
            keys of room_positions and whose value is the inferred likelihood.
        """
        likelihood = dict()
        for pos in room_positions.keys():
            likelihood[pos] = 0
            for recv in known_hosts.values():
                for gain in range(32):
                    p                = self.cdata[(recv,gain,pos)]
                    n,x              = self.obsman.get(tag,recv,gain)
                    likelihood[pos] += logbinomial(x, n, p)
                    
        lowest = min(likelihood[x] for x in room_positions.keys())
        
        for x in room_positions.keys():
            likelihood[x] -= lowest 
        
        return likelihood