"""
    This module contains helper functions specific to this thesis.  The
    only function of note is the RoomContour function, which makes a
    contour plot of the room, showing the geometry and contours of each
    point defined.
"""
from Thesis.constants import room_positions, room_geometry, room_dimensions
from Visualization.helpers import contour

def PointLine(p1,p2,zval=0.0,step=0.1):
    """
        Creates a set of 3D points with a static z component (default 0.0) that
        follow a line defined by the points p1 and p2.  The number of points
        returned depends on the value of the step variable.
    """
    # Create a set which will become the result, the set should initially contain the two end points
    result = set([(p1[0],p1[1],zval),(p2[0],p2[1],zval)])
    
    # Assume that p1 and p2 are good starting and ending points respectively
    x,y   = p1
    xf,yf = p2
    
    # Ensure that the lesser of the starting points is (x,y), depending on which axis we will increment along  
    if (xf - x != 0 and x > xf) or (xf - x == 0 and y > yf):
        x,y = p2
        xf,yf = p1
    
    # Calculate the x,y components of the distances between the points
    dx = xf - x
    dy = yf - y
    
    # if the points are the same the result is already taken care of
    if dx == 0 and dy == 0:
        return result
    if dx == 0:
        # the points are parallel to the vertical axis, increment along the vertical axis
        while y + step < yf:
            y += step
            result.add( (x,y,zval) )
    else:
        # the points have different x values, increment along the horizontal axis
        m = dy/dx
        while x + step < xf:
            x += step
            y += m * step
            result.add( (x,y,zval) )
    return result

def GeometryPoints(xstep=0.5):
    """
        Returns a set of 3D points which approximate the geometry of the room.
        Each point has a z-value of 0.  The number of points depends on the value
        of the xstep variable.
    """
    result = set()
    for line in room_geometry:
        pt1 = (line[0][0], room_dimensions[1] - line[0][1])
        pt2 = (line[1][0], room_dimensions[1] - line[1][1])
        for point in PointLine(p1=pt1, p2=pt2, step=xstep):
            result.add( point )
    return result

def RoomContour(posdata,geopoints,**kwargs):
    """
        Creates a contour plot visualization of the spatial points in the room.
        
        The room geometry will be visualized as a series of points.  These points, 
        defined in the geopoints variable must be an iterable of tuples with three
        components each, consider using the GeometryPoints function defined in this 
        module to provide these.
        
        The posdata variable defines the contour values at each point in the room.
        A mapping of the position number to the contour value to be used is 
        expected from this variable.  This function uses the room_positions global
        from the Thesis.constants module to get the XY values of each position.
        
        For details about the drawing method used consult the contour() function 
        defined in the Visualization.helpers module.
        
        The figure number used by pylab will be returned by this function.
    """
    
    # define a set of points which will be the values of every position
    pospoints = set()
    
    # for every known position lets define a point
    for pos,(x,y) in room_positions.items():
        # define the X, Y and Z values.  Because of the visualization method the Y 
        # value must be relative to the bottom of the room, not the top.  If the Z
        # value is not defined in posdata then use a zero value.
        xval = x
        yval = room_dimensions[1] - y
        zval = posdata.get(pos, 0.0)
        
        point = (xval, yval, zval)
        pospoints.add(point)
    
    # define all points that will be visualized as the union of the pospoints and geopoints set
    allpoints = pospoints.union( geopoints )
    
    # define the range of expected variables for the contour plot
    range_x = (0.0, room_dimensions[0])
    range_y = (0.0, room_dimensions[1]) 
    
    # return the figure number, returned by the contour plot function
    return contour(allpoints, xrange=range_x, yrange=range_y, include_bounds=False, **kwargs)
    
