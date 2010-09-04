"""
    This script visualizes calibration data as a line plot with X axis being the
    position number and Y axis being the probability of detection.  Each
    receiver defined in Thesis.constants will be visualized as its own line.
    
    Command Line Options
        --vis-dump            Write the plots to separate PNG files.
        
        --vis-prefix          When writing to PNG files prepend this
                              onto the filenames.
                              Default: None
    
        --legend              When creating the plots add a legend to
                              show which line corresponds to which receiver.
"""
from Positioning.DataSource.CalibrationFile import ParseCalibrationFile
from Thesis.constants import known_hosts, room_positions

from itertools import izip
from getopt import getopt

import sys, pylab, time

if __name__ == "__main__":
    ## A function to print usage
    ##-------------------------------------------------------------------------
    def usage(error):
        print "Error: %s\n" % error
        print "Usage: %s " % (sys.argv[0])
        print "\t<--calibration-file=FILE> [--position=INTLIST]"
        print "\t[--vis-dump] [--vis-prefix=STRING] [--legend]"
        sys.exit(1)
        
    ## Start by parsing the command line arguments
    ##-------------------------------------------------------------------------
    options = [
        "calibration-file=","position=","vis-dump","vis-prefix=","legend"
        ]
    
    optlist, args = getopt(sys.argv[1:], '', options)
    optlist = dict(optlist)
    
    CalibrationFile = optlist.get("--calibration-file")
    
    default         = ",".join([str(x) for x in room_positions.keys()])
    PosList         = [int(x) for x in optlist.get("--position", default).split(",")]
    
    VisDump         = optlist.has_key("--vis-dump")
    VisPrefix       = optlist.get("--vis-prefix","")
    
    UseLegend       = optlist.has_key("--legend")
        
    if not CalibrationFile:
        usage("No calibration data file specified.")
    
    ## Parse the data and visualize it 
    ##-------------------------------------------------------------------------
    data = ParseCalibrationFile(CalibrationFile)
    
    for pos in PosList:
        lines = [[data[(host,g,pos)] for g in range(32)] for host in known_hosts.values()]
            
        pylab.ion()
        pylab.figure(1)
        pylab.ioff()
            
        pylab.clf()
            
        pylab.plot(range(32),[prob for prob in izip(*lines)])
        
        pylab.xlim(0,31)
        pylab.ylim(0,1)
    
        if UseLegend:
            pylab.legend(known_hosts.keys())
        pylab.grid()
        
        pylab.xlabel("Gain Level")
        pylab.ylabel("Probability of Detection")
        pylab.title("Gain vs Probability for Position %d" % pos)
        
        pylab.draw()
        
        if VisDump:
            pylab.savefig("%sPos%0.2d" % (VisPrefix,pos))