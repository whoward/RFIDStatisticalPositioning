"""
    The purpose of this script is to measure the probability of detecting
    a SINGLE TAG at a SINGLE POSITION (STSP).
    
    Command Line Options:
        --receiver-rate       Sets the number of seconds between each
                              receiver sampling.
                              Default: 1 second
                              
        --receiver-samples    The number of samples between power level
                              changes for the receiver.
                              Default: 100 samples
"""
#Authors Note:  To improve the efficiency of the calibration period
# it should be possible to develop a MTSP AND MTMP calibration script
# MTSP: Multiple Tag Single Position
# MTMP: Multiple Tag Multiple Position)

from Positioning.DataSource.CalibrationFile import CalibrationFileWriter
from Protocol.GAORfidReceiver import Server
from Thesis.constants import known_hosts, known_tags
from tests import SimpleStatsTest
from getopt import getopt

import sys, threading

# Use this lock to make sure that only one thread attempts to access the file
# at the same time.
FileLock = threading.RLock()

class CalibrationThread(threading.Thread):
    def __init__(self, ID, pos, writer, connection, rate, count):
        self.id = ID
        self.pos = pos        
        self.rate = rate
        self.count = count
        
        self.writer = writer
        self.connection = connection
        
        threading.Thread.__init__(self)
    
    def run(self):
        recv = self.connection.addr
        
        ## Go through all power levels, running the simple statistics test to get
        ## a detection count at each power level.
        results = []
        for gain in range(32):
            print "INFO: Receiver %s is running gain=%d calibration set." % (recv,gain)
            x = SimpleStatsTest(n=self.count,t=self.rate,g=gain,id=self.id,con=self.connection)
            results.append(x)
        
        ## Notify the user that the calibration process for this position has
        ## completed, then write all the data to the calibration file.
        print "INFO: Receiver %s has finished calibration." % recv
        sys.stdout.write("\a")
        sys.stdout.flush()
        
        FileLock.acquire(True)
        try:
            for g in range(32):
                self.writer.writeCalibrationData(receiver=recv, rate=self.rate, gain=g, position=self.pos, 
                                                        samples=self.count, detections=results[g])
            self.writer.flush()
        finally:
            FileLock.release()

if __name__ == '__main__':    
    ## A function to print usage
    ##-------------------------------------------------------------------------
    def usage(error):
        print "Error: %s\n" % error
        print "Usage: %s " % (sys.argv[0])
        print "\t<--tag-id=ALIAS|ID> <--position=INT>"
        print "\t[--receiver-rate=FLOAT] [--receiver-samples=INT]"
        sys.exit(1)
        
    ## Start by parsing the command line arguments
    ##-------------------------------------------------------------------------
    options = [
        "tag-id=","position=","--receiver-rate=","--receiver-samples="
        ]
    
    optlist, args = getopt(sys.argv[1:], '', options)
    optlist = dict(optlist)

    id  = optlist.get("--tag-id")
    pos = int(optlist.get("--position","-1"))
    
    rate  = float(optlist.get("--receiver-rate", 1))
    count = int(optlist.get("--receiver-samples", 100))
        
    if not id:
        usage("No tag specified.")
    if pos < 0:
        usage("Position not specified or is invalid")
        
    ## Open a writer object for this tag, retrieve the actual id for the alias
    ##-------------------------------------------------------------------------
    writer = CalibrationFileWriter("Tag%s.cali" % id)
    
    if id in known_tags.keys():
        id = known_tags.get(id)
    
    print "INFO: Starting Server"
    serv = Server()
    serv.connect()
    
    ## Wait until the maximum number of connections has been reached
    for i in range( len(known_hosts.keys()) ):
        con = serv.getNextConnection()
        print "INFO: Connected by receiver %s on port %d" % (con.addr, con.port)
        
        thread = CalibrationThread(id,pos,writer,con,rate,count)
        thread.start()
        
    print "INFO: Maximum connections reached."
    
    