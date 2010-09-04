"""
    This module contains the classes and functions to handle the protocol used
    by the GAO RFID Receivers . 
"""
import struct, threading, time, socket

SENSOR_TYPE = {0x43: 'CARD', 0xBB: 'TEMP', 0xCC: 'VIBR'}

class Connection(object):
    """
        The Connection class handles TCP/IP communication between the server and the
        RFID Receiver.  The class SHOULD be thread safe.  This class does not handle
        Active mode at all as that model implies a listening thread while Passive 
        does not.
        
        This class DOES NOT concern itself with network issues that may arise and
        SHOULD NOT be used in a non-experimental environment in any situation.  It
        also does not concern itself with time synchronization or other distributed
        computing problems.  Timestamps recorded in observations will always be
        server time.
    """
    def __init__(self, address, connection):
        """
            This module contains a DataSource implementation to handle parsing data from
            Creates a Connection instance.
            
            The address variable is expected to be a tuple of length 2.  The first 
            element should be the IP address and the second element should be the port.
            
            The connection variable is the socket object itself that allows communication
            over TCP/IP.
        """
        self.conn = connection
        self.conn.settimeout(20)
        self.addr = address[0]
        self.port = address[1]
        
        self.lock = threading.RLock()
        
        self.setMode("passive")

    def __del__(self):
        self.conn.close()
        del(self.conn)
    
    def send(self, length, command, content=[]):
        """
            This method sends a general command to the RFID Receiver.  This method was
            only kept public for debugging purposes.
            
            The length variable is the integer length of the content.  This variable
            appears to always be equal to 48 but is included for possible future
            support.
            
            The command variable should be the protocol's command ID number for the
            intended command.
            
            The content variable should be an array of bytes to send to the receiver
            as the content buffer.
        """
        logo    = "BISA_RFID\0"
        version = struct.pack("BB", 0, 1)
        cmd     = struct.pack("H", command)
        cmdlen  = struct.pack("H", length)
        
        xc = 32 - len(content)
        c = "".join(struct.pack("B",i) for i in content) + struct.pack("x"*xc)
        
        self.conn.send(logo + version + cmdlen + cmd + c)
        #self.conn.flush()
        
    def setMode(self, mode, T1=1, T2=15):
        """
            This function sets the data retrieval mode of the RFID Receiver.
            
            The mode variable should be a string with a value of either "active" or 
            "passive".
            
            T1 is an integer being the minimum time between data pushes (active mode)
            
            T2 is an integer being the maximum time between data pushes (active mode)
        """
        if mode not in ("active","passive"):
            raise Exception("Illegal mode")
        
        self.lock.acquire(True)
        self.mode = mode
        if self.mode is "active":
            self.send(length=48, command=0xA0, content=[0,T1,T2])
        else:
            self.send(length=48, command=0xA0, content=[1])
        self.lock.release()

    def setGain(self, gain):
        """
            This function sets that gain level of the receiver.
            
            Gain should be an integer in the range of 0 to 31 inclusive.
        """
        if gain not in range(32):
            raise Exception("Illegal gain")
        
        self.lock.acquire(True)
        
        self.send(length=48, command=0x71, content=[0,gain])
        time.sleep(0.001)
        
        self.lock.release()
    
    def getGain(self):
        """
            This function requests the receiver to return the current gain value.
        """
        self.lock.acquire(True)
    
        self.send(length=48, command=0x72)
        time.sleep(0.001)
        result = self.parseMessage()
        
        self.lock.release()
        return ord( result['content'][1] )
        
    def getData(self):
        """
            This function requests the receiver to return whatever is in its data
            buffer at the point where it receives the request.
        """
        self.lock.acquire(True)
        
        self.send(length=48, command=0x15)
        time.sleep(0.001)
        result = self.parseMessage()
        
        self.lock.release()
        
        return self.parseReadings(result['buf'])
    
    def parseMessage(self):
        """
            This function receives a response structure from the socket and parses it.
            It does not need to be public but is left so for debugging and experimental 
            purposes.
            
            The value returned will be a dictionary with keys: logo, ver, len, content,
            cmd, buf.
        """
        data_logo = self.conn.recv(10)
        data_ver  = self.conn.recv(2)
        data_len  = self.conn.recv(2)
        data_cmd  = self.conn.recv(2)
        data_cont = self.conn.recv(32)
        
        length  = ord(data_len[0]) + ord(data_len[1])*256 
        version = ord(data_ver[1]) + ord(data_ver[0])*256
        command = ord(data_cmd[0]) + ord(data_cmd[1])*256
        
        data_buffer = []
        if length > 48:
            data_buffer = self.conn.recv(length - 48)
        
        return dict(logo=data_logo, ver=version, len=length, 
                        content=data_cont,cmd=data_cmd, buf=data_buffer)
        
    def parseReadings(self, buf):
        """
            This function attempts to parse tag readings from the data buffer
            which is the 'buf' part of the dictionary returned by the 
            parseMessage() method.  This function does not need to be public
            but is left so for debugging and experimental purposes.
            
            The value returned is a list of dictionaries containing the parsed
            readings of each detected tag.  The keys of these dictionaries will
            be 'id', 'type' and 'reading'.
        """
        retval = []
        count = int(len(buf) / 13)
        
        for i in range(count):
            x = buf[13*i:(13*i+13)]
            
            (DATA, ST_B) = struct.unpack("BB", x[0:2])
        
            TYPE = SENSOR_TYPE.get(DATA, "UNKNOWN")
            
            TAG_ID = []
            READING = None
            
            if TYPE == 'CARD' or TYPE == 'VIBR':
              TAG_ID = struct.unpack("BBBBBB", x[2:8])        
            elif TYPE == 'TEMP':
              TAG_ID = struct.unpack("BBBB", x[2:6])          
              (T_A,T_B) = struct.unpack("BB", x[6:8])
              
              N  = T_B & 0xF0
              TB = T_B & 0x0F
                        
              READING = float(T_A) + 0.1 * float(T_B) * (N and -1 or 1)                      
              
            TAGID_STR = "".join("%.2x" % x for x in TAG_ID)
            
            retval.append( dict(id=TAGID_STR,type=TYPE,reading=READING) )
            
        return retval



class Server(object):
    """
        The server class starts a server socket on port 8900 and will listen for
        incoming connections when the getNextConnection() method is called.
        
        The socket will not be opened until the connect() method is called, which
        can be subsequently cleaned up later by calling the disconnect() method.
    """
    def __init__(self,port=8900):
        self.port = port     
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []
        self.connected = False
        
    def __del__(self):
        for i in self.connections:
            del(i)
        
        if self.connected:
            self.disconnect()
            
        del(self.sock)
            
    def getNextConnection(self):
        """
            Accepts the next connection and returns the Connection object associated
            with it.
        """
        conn, addr = self.sock.accept()
        next = Connection(connection=conn, address=addr)
        self.connections.append(next)
        return next
        
    def connect(self):
        self.sock.bind(('',self.port))
        self.sock.listen(5)
        self.connected = True
        
    def disconnect(self):
        self.sock.close()
        self.connected = False
        
