"""
    This script makes use of a defined data source to receive observations
    and infer the likelihood of a tag existing at every tag defined in
    the Thesis.constants module.
    
    The data source is defined by command line options:
        If --observation-file is specified then this script will read all
        data from the observation file specified.
        
        If --simulate is specified then the script will simulate
        observations for the tag specified by --tag-id using the
        calibration data specified.
        
        If neither is specified the script will start up a receiver server
        and wait for connections from incoming receivers.
    
    
    Command Line Options:
        --observation-file    Specifies a file to read observations from.
                              Default: None
        
        --simulate            Specify a list of comma separated positions
                              to simulate a tag existing at.
                              Default: None
                              
        --simulate-mobility   The number of observations between the tag
                              moving to the next position in the list
                              specified in the --simulate option.
                              Default: 500 observations
        
        --receiver-rate       Sets the number of seconds between each
                              receiver sampling.
                              Default: 1 second
                              
        --receiver-samples    The number of samples between power level
                              changes for the receiver.
                              Default: 100 samples
        
        --window-size         Specifying a window size causes the script
                              to use a sliding window of observations
                              to infer the tag's location.  Observations
                              not in the range of [now - value, now] are
                              not included in the inference.
                              Default: None
                              
        --vis-step            The number of observations between
                              visualization updates.
                              
        --vis-dump            When the visualization is updated write
                              it to a png file.
                              
        --vis-filled          When drawing the visualization use a colour
                              gradient rather than the contour lines.
        
        --obs-dump-file       Write every incoming observation to this 
                              output observation dump file as well as
                              to the visualization.
"""
from Positioning.DataSource.ReceiverServer import ReceiverServer
from Positioning.DataSource.DumpFile import DumpFileReader, DumpFileWriter
from Positioning.DataSource.Simulator import Simulator

from Thesis.constants import *
from getopt import getopt
from Queue import Queue

from Positioning.ObservationManager import Dynamic, Static
from Positioning.InferenceEngine import InferenceEngine

from Visualization.room import *
from itertools import izip

import sys, time, pylab

if __name__ == '__main__':

    ## A function to print usage
    ##-------------------------------------------------------------------------
    def usage(error):
        print "Error: %s\n" % error
        print "Usage: %s " % (sys.argv[0])
        print "\t<--tag-id=ID> <--calibration-file=FILE>"
        print "\t[--observation-file=FILE | --simulate=POSLIST]"
        print "\t[--receiver-rate=FLOAT] [--receiver-samples=INT]"
        print "\t[--simulate-mobility=INT] [--window-size=FLOAT]"
        print "\t[--vis-step=INT] [--vis-dump] [--vis-filled]"
        print "\t[--obs-dump-file=FILE]"
        sys.exit(1)
    
    ## Start by parsing the command line arguments
    ##-------------------------------------------------------------------------
    options = [
        "window-size=","calibration-file=","observation-file=",
        "simulate=","simulate-mobility=","tag-id=","vis-step=",
        "vis-dump","vis-filled","receiver-rate=","receiver-samples=",
        "obs-dump-file="
        ]
    
    optlist, args = getopt(sys.argv[1:], '', options)
    optlist = dict(optlist)
    
    WindowSize = float(optlist.get("--window-size","-1"))
    
    ShowConverge = optlist.has_key("--show-converge")
    
    VisualizationRate = int(optlist.get("--vis-step","1000"))
    VisualizationDump = optlist.has_key("--vis-dump")
    VisualizationFill = optlist.has_key("--vis-filled")
    
    CalibrationFile = optlist.get("--calibration-file")
    ObservationFile = optlist.get("--observation-file")
    
    SimulatePositions = optlist.get("--simulate",False)
    if SimulatePositions:
        SimulatePositions = [int(x) for x in SimulatePositions.split(",")]
    SimulateMobility = int(optlist.get("--simulate-mobility","500"))
    
    DumpObservationsFile = optlist.get("--obs-dump-file")
    
    ReceiverRate = float(optlist.get("--receiver-rate", 1))
    ReceiverSamples = int(optlist.get("--receiver-samples", 100))
    
    TagID = known_tags.get(optlist.get("--tag-id"))
    if TagID is None:
        usage("No Tag ID Specified")
    if CalibrationFile is None:
        usage("No Calibration File Specified") 
        
    ## Open the calibration data file and parse the data
    ##-------------------------------------------------------------------------
    CalibrationFile = open(CalibrationFile, "r")
    CalibrationData = dict()
    try:
        for line in CalibrationFile:
            (host,t,g,n,p,x) = line.split(",")
            t,g,n,p,x = (float(t),int(g),int(n),int(p),int(x))
        
            CalibrationData[(host,g,p)] = float(x)/float(n)
    finally:
        CalibrationFile.close()
        
    ## Create an ObservationsManager for the Data Source to write to
    ##-------------------------------------------------------------------------
    if WindowSize > 0:
        obsman = Dynamic.ObservationsManager(WindowSize)
    else:
        obsman = Static.ObservationsManager()
    obsman.start()
    
    ## Define the observations queue based on whether or not dumping was set
    ##-------------------------------------------------------------------------
    if DumpObservationsFile:
        DumpQueue = Queue()
        ObservationsQueue = (obsman, DumpQueue)
        
        DumpWriter = DumpFileWriter(filename=DumpObservationsFile, queue=DumpQueue)
        DumpWriter.open()
        DumpWriter.start()
    else:
        ObservationsQueue = obsman
        
    ## Instantiate the Data Source
    ##-------------------------------------------------------------------------
    if ObservationFile:
        DataSource = DumpFileReader(queue=ObservationsQueue,filename=ObservationFile)
    elif SimulatePositions:
        DataSource = Simulator(queue=ObservationsQueue, cali=CalibrationData, tag=TagID,
                                    movement=SimulatePositions, mobility=SimulateMobility)
    else: 
        DataSource = ReceiverServer(queue=ObservationsQueue,t=ReceiverRate,n=ReceiverSamples)
    
    ## Create an InferenceEngine
    ##-------------------------------------------------------------------------
    iengine = InferenceEngine(obsman,CalibrationData)
    
    ## Draw the visualization and wait the refresh rate time before drawing again
    ##-------------------------------------------------------------------------        
    class Visualizer():
        def __init__(self,tag,obsman):
            self.visnum = 0
            self.tag = tag
            self.obsman = obsman
            self.geodata = GeometryPoints(0.25)
            
        def notify(self,subject):
            argmax = lambda array: max(izip(array, xrange(len(array))))[1]
            
            values = iengine.infer(self.tag)
            ipos = argmax(values.values())
            
            plotTitle = "%d Observations [Maximal Likelihood=%s]" % (self.obsman.observationCount,ipos)
            
	    RoomContour(values,self.geodata,figure_number=1,title=plotTitle,legend=False,xlabel="",ylabel="",filled=VisualizationFill)
            
            if VisualizationDump:
                pylab.savefig("%06d.png" % self.visnum)
            
            self.visnum = self.visnum + 1

    visualize = Visualizer(TagID,obsman)    
    obsman.addUpdateListener(visualize, VisualizationRate)
    visualize.notify(None)
    DataSource.start()
