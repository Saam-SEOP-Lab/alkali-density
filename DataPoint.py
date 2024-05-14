

class DataPoint: 
    """
    A class used construct a generic data point with numerical x and y values. 

    ...

    Attributes
    ----------
        x_val : float
            The x value of the data point.   
        y_val : float
            The y value of the data point. 
        y_err : float
            The error in the y value. Defaults to 0. 

    Methods
    -------
    __init__(self, x_val, y_val, y_err=0)
        Creates a DataPoint object.
    """
     
    def __init__(self, x_val, y_val, y_err=0):
        """
        Creates a DataPoint object.

        Parameters
        ----------
        self : DataPoint
            the DataPoint object to be created. 
        x_val : float
            The x value of the data point.   
        y_val : float
            The y value of the data point. 
        y_err : float
            The error in the y value. Defaults to 0. 


        Returns
        -------
        VoltageReading
            Returns a new VoltageReading object.  
        """
        self.x_val = x_val
        self.y_val = y_val
        self.y_err = y_err

    
class VoltageReading:
    """
    A class used to record a voltage reading and the timestamp at which that reading was taken. 

    ...

    Attributes
    ----------
        v : float
            The voltage reading from the oscilloscope.   
        tstamp : float
            The timestamp for the reading.   

    Methods
    -------
    __init__(self, v, tstamp)
        Creates a VoltageReading object.
    """

    def __init__(self, v, tstamp):
        """
        Creates a VoltageReading object.

        Parameters
        ----------
        self : VoltageReading
            the VoltageReading object to be created. 
        v : float
            The voltage reading from the oscilloscope.   
        tstamp : float
            The timestamp for the reading.   

        Returns
        -------
        VoltageReading
            Returns a new VoltageReading object.  
        """
        self.voltage = v
        self.timestamp = tstamp
    
