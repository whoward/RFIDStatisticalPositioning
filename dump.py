"""
    This script starts up a server which accepts connections from receivers
    and write observations received to a file.
    
    Command line options:
        --max-observations    Specifying this value will cause the server
                              to shut down after the number of observations
                              have been read in.
                              Default: Unlimited
        
        --receiver-rate       Sets the number of seconds between each
                              receiver sampling.
                              Default: 1 second
                              
        --receiver-samples    The number of samples between power level
                              changes for the receiver.
                              Default: 100 samples
"""
from Positioning.DataSource.ReceiverServer import ReceiverServer
from Positioning.DataSource.DumpFile import DumpFileWriter

from Queue import Queue
from getopt import getopt

import sys, threading
    
if __name__ == '__main__':
    
    ## A function to print usage
    ##-------------------------------------------------------------------------
    def usage(error):
        print "Error: %s\n" % error
        print "Usage: %s " % (sys.argv[0])
        print "\t<--observation-dump-file=FILE> [--max-observations=INT]"
        print "\t[--receiver-rate=FLOAT] [--receiver-samples=INT]"
        sys.exit(1)    
    
    ## Start by parsing the command line arguments
    ##-------------------------------------------------------------------------
    options = [
        "observation-dump-file=","max-observations=",
        "receiver-rate=","receiver-samples="
        ]
    
    optlist, args = getopt(sys.argv[1:], '', options)
    optlist = dict(optlist)
    
    DumpFile = optlist.get("--observation-dump-file")
    MaxObservations = int(optlist.get("--max-observations",-1))
    
    ReceiverRate = float(optlist.get("--receiver-rate", 1))
    ReceiverSamples = int(optlist.get("--receiver-samples", 100))
    
    if not DumpFile:
        usage("No observation dump file specified.")
    
    ## Start up receivers 
    ##-------------------------------------------------------------------------    
    ObservationQueue = Queue()
    
    rserver = ReceiverServer(queue=ObservationQueue, t=ReceiverRate, n=ReceiverSamples)
    rserver.start()
    
    class EchoWriter(threading.Thread):
        def __init__(self, filename, queue, max):
            self.queue   = queue
            self.max     = max
            self.count   = 0
            
            self.file    = DumpFileWriter(filename)
            self.file.open()
            
            self.running = True
            
            threading.Thread.__init__(self)
            
        def stop(self):
            self.running = False
            self.file.close()
            
        def run(self):
            while self.running:
                if self.max >= 0 and self.count >= self.max:
                    print "Done writing observations."
                    break
                
                try:
                    obs = self.queue.get(True,1.0)
                    
                    self.count += 1
                    if self.count % 100 == 0:
                        print "Wrote %d observations to file" % self.count
                    
                    self.file.writeObservation(obs)
                except:
                    continue
            
            self.stop()
            sys.exit(0)
    
    writer = EchoWriter(filename=DumpFile, queue=ObservationQueue, max=MaxObservations)
    writer.start()

    ##  Wait until the user 
    ##-------------------------------------------------------------------------
    print "Started the server, writing to file"
    print "PRESS <ENTER> TO SHUTDOWN THE PROGRAM"
    sys.stdin.readline()
    writer.file.close()
    
    sys.exit(0)