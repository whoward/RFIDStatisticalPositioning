"""
    This module contains a DataSource implementation to handle parsing and 
    writing data to and from an Observation Dump File.  
    
    The file is a comma separated values file with some special features.
        - Whitespace lines are ignored
        - Lines starting with a '#' character are ignored (for commenting)
    
    Each line of data represents a single observation. The expected columns
    are:
        Data Timestamp      : floating point number (Epoch Timestamp)
        Receiver IP Address : String IP address (not validated)
        Gain Level          : integer
        Detected Tags List  : Semicolon (;) separated list        
"""
import threading, re, time

class DumpFileWriter(threading.Thread):
    """
        This class handles simply writing data to an observation file.  It
        can be used to continually read from a Queue and write to the file
        or to manually write observations out one after another.
    """
    def __init__(self,filename,queue=None):
        """
            Constructs a DumpFileWriter which will write to the file specified
            by 'filename'.  If a queue is provided then once the thread is
            started the writer will read observations from the queue to write
            immediately to the file.
            
            The file must be opened before writing so it is necessary to call
            the open() method before calling any other method.
        """
        self.__queue = queue
        self.__filename = filename
                
        self.__lock = threading.RLock()
        self.__running = False
        
        threading.Thread.__init__(self)
        
    def run(self):
        """
            If a queue is defined the thread will enter a loop to continually
            read observations from the queue and write them to file until the
            close() method is called. 
        """
        # Do nothing if a queue is not defined
        if self.__queue is None:
            return
        
        # If the file is not open throw an exception
        if not self.__file:
            raise Exception("File not open")
        
        self.__running = True
        
        while self.__running:
            # Try for at max a second to get a reading, timeout is to allow thread interruption
            obs = None
            try:
                obs = self.__queue.get(block=True, timeout=1.0)
            except:
                continue
            
            # A reading was obtained so write it to the file
            self.__lock.acquire(True)
            try :
                if self.__running:
                    self.writeObservation(obs)
            finally:
                self.__lock.release()

    def writeComment(self,comment):
        """
            Write a comment to the file.
        """
        self.__file.write("# %s" % comment)
    
    def writeObservation(self, obs):
        """
            Writes a single observation line to the file.  Not thread safe.
        """
        # If the file is not open throw an exception
        if not self.__file:
            raise Exception("File not open")
        
        self.__file.write("%f,%s,%d,%s\n" % ( obs[3], obs[0], obs[1], ";".join(obs[2]) ))
        
    def open(self):
        """
            Opens the file for appending.  Adds a single comment line with
            the time the file was opened.
        """
        self.__lock.acquire(True)
        
        self.__file = open(self.__filename, "a", buffering=1024)
        self.__file.write("# Started Writing: %s\n" % time.ctime())
        self.__file.flush()
        
        self.__lock.release()
        
    def flush(self):
        """
            Causes the file to flush it's buffer.
        """
        self.__lock.acquire(True)
        self.__file.flush()
        self.__lock.release()
    
    def close(self):
        """
            Closes the file.  If the thread is running it will be stopped
            within one second.
        """
        self.__lock.acquire(True)
        self.__file.close()
        self.__running = False
        self.__lock.release()
 

class DumpFileReader(threading.Thread):
    """
        This class handles parsing data from a single observation dump
        file and putting that data onto a queue defined at construction.  As 
        this is intended to maintain the same interface as all other DataSource
        classes the DumpFile class extends the Thread class and must be started
        before data is retrieved.  The class is NOT thread safe.   
    """
    def __init__(self,queue,filename):
        """
            Constructs a DumpFile instance which will open the file defined by
            the 'filename' variable and when started will offer data to the
            queue defined by the 'queue' variable.
        """
        self.queue = queue
        self.file = open(filename, "r")
        
        threading.Thread.__init__(self)
    
    def run(self):
        # helper function to determine if a string split result is actually an empty list
        notags = lambda x : len(x) == 1 and len(x[0]) == 0
        
        while True:
            # Read a line in from the file
            line = self.file.readline()
            
            # If no line was read assume end of file and stop exeuction of this thread
            if not line:
                break
            
            # If the line is empty/whitespace or starts with a '#' character ignore it
            if line.startswith("#") or len(re.sub("\s+","",line)) == 0:
                continue
            
            # Split the line by commas (CSV file).  Then parse the individual columns.
            cols = line.split(",")
            time,recv,gain,tags = float(cols[0]), cols[1], int(cols[2]), cols[3].split(";")
            
            # If no tags were associated with this reading, then assign an empty list
            if notags(tags):
                tags = []
            
            # if the queue is iterable lets assume its a list of queues and
            # write the observation to every one of them
            if not hasattr(self.queue,'__iter__'):
                self.queue.put((recv,gain,tags,time))
            else:
                for queue in self.queue:
                    queue.put((recv,gain,tags,time))
