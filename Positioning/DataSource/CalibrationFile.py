"""
    This module contains a function and class to manage parsing data
    from and writing data to a calibration file.
"""
import re, time

def ParseCalibrationFile(filename):
    """
        Parses a calibration file and returns the calibration data as a
        dictionary whose key is a tuple whose components are the receiver,
        the power level, and the position.
    """
    CalibrationFile = open(filename, "r")
    CalibrationData = dict()
    try:
        for line in CalibrationFile:
            # If the line is empty/whitespace or starts with a '#' character ignore it
            if line.startswith("#") or len(re.sub("\s+","",line)) == 0:
                continue
            
            (recv,t,g,n,p,x) = line.split(",")
            t,g,n,p,x = (float(t), int(g), float(n), int(p), float(x))
        
            #TODO: include T term in key
            key = (recv,g,p)
            if CalibrationData.has_key(key):
                CalibrationData[key][0] += x
                CalibrationData[key][1] += n
            else:
                CalibrationData[key] = [x,n]
    finally:
        CalibrationFile.close()
        
    for key,(x,n) in CalibrationData.items():
        CalibrationData[key] = x / n

    return CalibrationData

class CalibrationFileWriter():
    """
        This class handles writing calibration data to a file.
    """
    def __init__(self,filename):
        self.__file = open(filename, "a", buffering=1024)
        self.__file.write("# Started Writing: %s\n" % time.ctime())
        pass
    
    def close(self):
        self.__file.close()
        
    def flush(self):
        self.__file.flush()
    
    def writeComment(self, comment):
        """
            Writes a comment line to the file
        """
        self.__file.write("# %s\n" % comment)
    
    def writeCalibrationData(self,receiver,rate,gain,position,samples,detections):
        """
            Writes a single line of calibration data to the file
        """
        self.__file.write("%s,%f,%d,%s,%d,%d\n" % (receiver,rate,gain,position,samples,detections))
