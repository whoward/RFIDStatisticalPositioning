"""
    This module defines a number of global constants which are used
    extensively throughout most of the modules in this thesis project.
"""


"""
    The known hosts global defines a mapping of the receiver aliases
    to their static IP Addresses in the experiment's private network.
"""
known_hosts = {
        "RECV_SW":"192.168.1.200",
        "RECV_SE":"192.168.1.201",
        "RECV_NW":"192.168.1.202",
        "RECV_NE":"192.168.1.203"
    }

"""
    The known tags global defines a mapping of the tag aliases to the
    radio frequency identification number that would be returned by the
    GAORfidReceiver.Driver class
"""
known_tags = {
        "A":"000000000080",
        "B":"000000000077",
        "C":"000000000076",
        "D":"000000000071",
        "E":"000000000079",
        "F":"000000000181",
        "G":"000000000075",
        "H":"000000000074",
        "I":"000000000073",
        "J":"000000000072"
    }

"""
    The room positions global defines the locations of the sampled
    points in the room with respect to the tiles on the floor (the
    actual measurements were not THAT important so the tiles served
    as a sufficient measurement tool).
    
    The layout i used in the code may look unusual at first but this
    is actually roughly the layout used in the room so it sort of
    makes sense.  Positions 16-22 were added a while after the layout
    was initially set down so I've just listed them rather than trying
    to insert them into this structure.
"""
room_positions = {
        0 : ( 2.25,  1.76),  1 : (5.25,  1.76), 2 : (8.25, 1.76),   3 : (11.25, 1.76),
                             4 : (5.25,  4.76), 5 : (8.25, 4.76),   6 : (11.25, 4.76),
        7 : ( 2.25,  8.24),  8 : (5.25,  8.24),                     9 : (11.25, 8.24),
        10: ( 2.25, 12.26),  11: (5.25, 12.26),                     12: (11.25,12.26),
        13: ( 2.25, 15.26),  14: (5.25, 15.26),                     15: (11.25,15.26),       
        16: ( 3.70, 15.26),
        17: ( 3.70, 12.26),
        18: ( 3.70,  8.24),
        19: ( 3.70,  1.76),
        20: ( 7.20,  2.00),
        21: ( 9.70,  2.50),
        22: (11.20,  3.50)
    }

"""
    The room dimensions global defines simply the X and Y dimensions
    of the room.
"""
room_dimensions = (13.33, 18.00)

"""
    The room geometry global defines a list of lines (2 points) that
    make up the geometry of the room during the experiment.  It is
    only used for visualization purposes.  
    
    The room was measured by the tiles on the floor (the dimensions 
    were not THAT important and the tiles were used to lay out the 
    positions anyways so it made sense).  The measurements were
    13.33 x 18.00 tiles.
"""
room_geometry = [
        # Room Boundaries
        (( 0.0,  0.0),   (13.3,  0.0)),     # North Wall
        (( 0.0,  0.0),   ( 0.0, 18.0)),     # West Wall
        (( 0.0, 18.0),   (13.3, 18.0)),     # South Wall
        ((13.3,  0.0),   (13.3, 18.0)),     # East Wall
        
        # West Desks
        (( 0.0,  4.0),   ( 1.3,  4.0)),
        (( 1.3,  4.0),   ( 1.3, 18.0)),
        
        # Center Desk
        (( 7.00, 8.50),  ( 7.00, 18.00)),
        ((10.00, 8.50),  (10.00, 18.00)),
        (( 7.00, 8.50),  (10.00,  8.50)),
        
        # Southern Cabinet
        (( 2.45, 16.75), ( 2.45, 18.00)),
        (( 5.45, 16.75), ( 5.45, 18.00)),
        (( 2.45, 16.75), ( 5.45, 16.75)),
        
        # Southeastern Cabinet
        ((12.70, 14.50), (13.30, 14.50)),
        ((12.70, 17.00), (13.30, 17.00)),
        ((12.70, 14.50), (12.70, 17.00)),
        
        # Northeastern Cabinet
        ((12.70,  1.00), (13.30,  1.00)),
        ((12.70,  3.50), (13.30,  3.50)),
        ((12.70,  1.00), (12.70,  3.50)),
        
        # Northern Cabinets
        (( 5.04,  0.66), ( 5.04,  0.00)),
        (( 8.36,  0.66), ( 8.36,  0.00)),
        (( 5.04,  0.66), ( 8.36,  0.66))
    ]