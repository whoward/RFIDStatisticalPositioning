Author(s)
==================
William Howard - http://william.howard.name
Dr. Ken Pu (Supervisor) - http://leda.science.uoit.ca

Description
==================
This is the polished version of the source code which I used to complete my
undergraduate thesis titled "A System for a Statistical-Based Positioning of
RFID Tags".  In order to have a thorough understanding of the source code
I suggest you read the thesis.

In more plain terms this project was created to find a way to have a computer
program take a guess at just where in a room an RFID tag actually is.

For those not aware RFID tags can be detected from a good distance by radio 
waves sent out by RFID Receivers.  The problem is that most RFID Receivers,
especially the inexpensive ones, only really give you one piece of 
information: whether a tag is near the receiver or not.

Another thing to note is that receivers do not have a radius of detection;
they will not always pick up tags in a perfect circle around them.  If, say,
you put a thick wall right beside the receiver there's a good chance it won't
pick up a tag that's on the other side of that wall.  This is where we come in.

Our project makes use of statistics to take an educated guess where a tag is.
What we do is we define a number of points in our room - we call them 
"positions" (and yes, I've made a big effort in keeping consistent with names
across the whole project).  Lets also assume you have more than one receiver
in the room - you can do it with just one but I suspect the results won't be
very accurate or interesting.  

For every one of these positions we'll use every receiver to check what the 
probability of detecting a tag at that position is and write it to a file 
(I name my sample ones using a scheme of TagX.cali).  Thats really all it
takes to get started.  From here we can place the tag down near any one of
these positions and start up the receivers.  They'll start telling us whether
or not they can detect the tag and we'll use statistics to find out how likely
it is that the tag is at EVERY one of our positions.

THATS THE BASICS

It DOES get A LOT more complicated than that.  For instance, the receivers
we used can change their power level which we take advantage of!  Theres a lot
of other things to consider and if you're interested read the thesis.


DATA FILES
==================
I've included dump files and calibration data which have been recorded right
from our own lab during our experiments.  Each of these data files have header
information in them that look like C comments (start with a # character).  
The header information will give you a bit more information about the details
of each file.

OBS Files:
	These are observation dump files.  Basically these hold a subset of
	recorded observations for a certain span of time and can be used to
	proxy for GAO RFID Receivers if you don't have them.  The file format
	is thoroughly described in the Positioning.DataSource.DumpFile module.

CALI Files:
	These contain calibration data for each tag by every one of our
	receivers.  Since we found each tag has its own probability of detection
	(though they seem to work with another tag's calibration data).  The
	file format is described thoroughly in the 
	Positioning.DataSource.CalibrationFile module.


FAQ
==================
Q: I'm interested in testing this in my own environment with my own RFID 
system, where do I start?

A: If you're using the GAO RFID Receivers we used in the development of
our thesis then you're in luck because it will be a LOT EASIER.  Skip
onto step two (below) if this is the case.

1) If you're not using the same receivers you may end up having a much
harder time because a lot of the intricacies of the GAO Receivers are
hardcoded into the source code.  For instance since our receivers have
32 discrete power levels enumerated 0-31 we use the python function
range(32) quite often.

You may be best off waiting to see if we later integrate some extensibility
into the project, which will let you choose which kind of receiver to use.

If you don't want to wait you have pretty much two options:
A) Hack into our source code to change the hardcoded values.
B) Write your own system using our code as reference.

2) You'll have to make changes to the Thesis.constants module.  This
contains the information relevant to our particular environment and its
referenced by a great many other files to work properly.  You'll need
to change the contents of the following constants:

A) known_hosts - since GAO's receivers don't use DHCP they'll always
	have a static IP address.  Use this dictionary to map an
	alias to the static IP address.

B) known_tags - Give a friendly alias name to every tag.  We used
	the letters of the latin alphabet to name ours.  Just map
	the alias to the Tag's ID.

C) room_positions - This may look weird at first but its pretty easy.
	As before its a dictionary.  Its mapping a position number to
	a set of XY coordinates representing the position in the room.
	This is only really used for the spatial contour plot so far.

D) room_dimensions - You need a width and a height for the whole room
	stored as a tuple.

E) room_geometry - more complicated.  This is used only for the spatial
	contour plot so its not INCREDIBLY important.  If you look at it
	its actually defining a set of lines.  Those lines get turned
	into points which you see on the spatial contour plot.  Basically
	this just makes your room look right on the visualization.

And that should be it!  Give it a shot!


Installation
==================
No installation is required.  This project makes use of the Python 2.5
interpreter which can be downloaded at http://www.python.org/

Be sure to install the libraries specified below, some parts of this project
will run without them but some wont (the ones which can make use of plots)

If you're interested in the receivers we used I would contact GAO.  Their
website at the time of writing was http://www.gaorfid.com/

The program should be able to execute without issues on any Python-supported
distribution of Microsoft Windows, GNU/Linux, and Mac OSX.  It has been 
tested on Ubuntu Linux 8.10 Hardy Heron and Microsoft Windows XP Home.

To make use of this project you can invoke any of the scripts.  Each script
has its own functional purpose:

	dump.py:
		Starts a receiver server, accepts connections and writes 
		observations to a observation dump file.

	infer.py:
		Can set up a stream of observations from one of three 
		possible data sources and then infer the likelihood of a 
		tag existing at every defined point from the observation 
		stream.  The inferred likelihood is then visualized using 
		a spatial contour plot.

	stsp-calibrate.py:
		Starts a receiver server, accepts connections and measures
		the probability of detecting a SINGLE TAG at a SINGLE 
		POSITION (STSP).

	VisualizeCalibrationLines.py:
		Takes a calibration file and visualizes probability data as 
		a line plot.

	VisualizeCalibrationRoom.py:
		Takes a calibration file and visualizes probability data as 
		a spatial contour plot.

Command line parameters are detailed in the headers of each script.

License
==================
The source code of this project is licensed under the GNU GPL v3.0 whose text is 
included as gpl-3.0.txt.

Libraries
==================
    Numerical Python v1.2.0 http://numpy.scipy.org/
	Used with Matplotlib to handle the plotting.

    Matplotlib v0.98.3 http://matplotlib.sourceforge.net/
	Used with numerical python to handle plotting.