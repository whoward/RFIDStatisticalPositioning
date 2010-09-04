"""
    This module contains a number of helper functions to visualize data plots
    easily.  The functions help provide abstraction from the drawing systems
    utilized.
"""
from matplotlib.mlab import griddata
import numpy, pylab, time

def contour(points, title="Untitled Plot", xlabel="Untitled X-Axis", ylabel="Untitled Y-Axis",
            legend=True, xrange=(0,100), yrange=(0,100), figure_number=None, include_bounds=True,
            filled=True):
    """
        This helper function creates a pylab figure for a contour plot from a 
        list of tuples of length 3.  This function returns the figure number 
        for the pylab figure.  To handle replotting set the figure_number to 
        the number returned by your original plotting function. 
    """
    
    # Create a figure or set it to the active figure
    pylab.ion()
    number = pylab.figure(figure_number).number
    pylab.ioff()
    
    # Clear the figure
    pylab.clf()
    
    # Transform the ordered triplets into a vector
    x = []
    y = []
    z = []
    
    for pt in points:
        x.append(pt[0])
        y.append(pt[1])
        z.append(pt[2])
        
    # Add the range points (xmin, ymin), (xmax, ymin), (xmin, ymax), (xmax, ymax)
    if include_bounds:
        x.extend([ xrange[0], xrange[1], xrange[0], xrange[1] ])
        y.extend([ yrange[0], yrange[0], yrange[1], yrange[1] ])
        z.extend([ 0,         0,         0,         0         ])
    
    # Wrap these in a numerical python array so we can use them in the visualization
    x = numpy.array(x)
    y = numpy.array(y)
    z = numpy.array(z)
    
    # Use linear interpolation on the points to get a normal grid
    xi = numpy.linspace(xrange[0], xrange[1], 100)
    yi = numpy.linspace(yrange[0], yrange[1], 100)
    zi = griddata(x,y,z,xi,yi)
    
    # Draw a filled contour plot
    if filled:
        pylab.contourf(xi,yi,zi, 15, cmap=pylab.cm.jet)
    else:
        pylab.contour(xi,yi,zi, 15, cmap=pylab.cm.gray)
    
    if legend:
        pylab.colorbar()
    
    # Mark the points on the contour plot
    pylab.scatter( x, y, marker='o', c='black', s=20)
    pylab.xlim( xrange[0], xrange[1] )
    pylab.ylim( yrange[0], yrange[1] )
    
    # Add some labels to the plot
    pylab.title(title)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    
    # Draw the plot
    pylab.draw()
    
    # Return the number
    return figure_number
    
if __name__ == '__main__':
    points = [
              [10,70,10], (20,50,20), (10,50,30), (10,30,40), (15,30,50), (50,30,60),
              (70,30,0),  (70,50,0),  (70,75,0)
             ]
    
    contour(points, legend=False)
    pylab.savefig("out.png")
