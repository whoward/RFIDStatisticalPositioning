"""
    This script visualizes calibration data as a contour plot and writes the 
    output to a PNG file.  The contour plot will include points to 
    approximate the room's geometry.
    
    Command Line Options:
        --receiver            Specifies a specific receiver to visualize.
                              Default: All receivers
        
        --gain                Specifies a specific power level to visualize.
                              Default: All gains.
        
        --legend              When creating plots add a legend which shows
                              a mapping of the contour levels to the
                              probability of detection.
                              
        --filled              When creating the contour plot draw a colour
                              gradient rather than the contour lines.
                              
        --vis-prefix          When writing to PNG files prepend this to the
                              filenames.
                              Default: None    
"""
from Visualization.room import RoomContour, GeometryPoints
from Thesis.constants import *

from itertools import izip
from getopt import getopt

import sys, time, pylab

if __name__ == "__main__":
    
    ## A function to print usage
    ##-------------------------------------------------------------------------
    def usage():
        print "Usage: %s " % (sys.argv[0])
        print "\t<--calibration-file=FILE> [--receiver=ALIAS|IP] [--gain=INT]"
        print "\t[--legend] [--vis-prefix=STRING] [--filled]"
        sys.exit(1)
    
    ## Start by parsing the command line arguments
    ##-------------------------------------------------------------------------
    options = ["calibration-file=","receiver=","gain=","legend","vis-prefix=","filled"]
    
    optlist, args = getopt(sys.argv[1:], '', options)
    optlist = dict(optlist)
    
    CalibrationFile = optlist.get("--calibration-file")
    Receiver        = optlist.get("--receiver")
    Gain            = int(optlist.get("--gain","-1"))
    UseLegend       = optlist.has_key("--legend")
    FilledContour   = optlist.has_key("filled")
    
    DumpPrefix      = optlist.get("--vis-prefix","")
    
    if CalibrationFile is None:
        print "No Calibration File Specified"
        usage()
    
    
    ##########
    
    argmax = lambda array: max(izip(array, xrange(len(array))))[1]
    
    CalibrationFile = open(CalibrationFile, "r")
    CalibrationData = dict()
    
    try:
        for line in CalibrationFile:
            (host,t,g,n,p,x) = line.split(",")
            t,g,n,p,x = (float(t),int(g),int(n),int(p),int(x))
        
            CalibrationData[(host,g,p)] = float(x)/float(n)
    finally:
        CalibrationFile.close()
    
    # Determine which receivers to iterate through, depending on command line args
    recvs = known_hosts.values()
    if Receiver:
        recvs = [ known_hosts.get(Receiver, Receiver) ]
    
    # Determine which gains to iterate through, depending on command line args
    gains = range(31,-1,-1)
    if Gain >= 0:
        gains = [ Gain ]
    
    # Pre-calculate the geometry points
    geodata = GeometryPoints(0.25)
    
    # Go through every receiver and every gain
    for gain in gains:
        for recv in recvs:
    
            # Get tuples for each position
            values = dict()
            for pos in room_positions.keys():
                values[pos] = CalibrationData.get((recv,gain,pos))
            
            # Create the plot and save it
            plotTitle = "Calibration Data for %s at gain %d" % (recv,gain)
            RoomContour(values,geodata,figure_number=1,title=plotTitle,xlabel="",ylabel="",legend=UseLegend,filled=FilledContour)
            
            pylab.savefig( "%s%s-G%0.2d.png" % (DumpPrefix, recv, gain) )
    