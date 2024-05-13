import numpy as np

#class for storing a data set to be plotted on an x y scatter plot
class plotable:
    """
    A class used plot rotation and magnetic field data for the purpose of determining density.  

    ...

    Attributes
    ----------
    x :  numpy array
        an array containing the magnetic field values (in Gauss) 
    y :  numpy array
        an array containing the rotation values (in radians)
    laser_wavelength : float
        the wavelength (in cm) of the probe laser used . 
    optical_length : float  
        the length of the path of the laser through the cell used (in cm). 
    x_error : numpy array
        the error in the magnetic field values (in Gauss). Set to [] by default.  
    y_error : numpy array
        the error in the rotation values. Set to [] by default.

    Methods
    -------
    __init__(self, x, y, laser_wavelength, optical_length, x_error = [], y_error = [])
        Creates new plotable object.
    get_plotable_subset(self, type, index1, index2=None)
        Creates a subset of the original data. Typically used to drop off the first datapoint
    """
    
    def __init__(self, x, y, laser_wavelength, optical_length, x_error = [], y_error = []):
        """
        Creates a new plotable object.

        Parameters
        ----------
        self : plotable
            The new plotable object being created. 
        x : numpy array
            An array containing the magnetic field values (in Guass)
        y : numpy array
            An array containing the rotation values (in radians)
        laser_wavelength : float
            the wavelength (in cm) of the probe laser used 
        optical_length : float
            the length of the path of the laser through the cell used (in cm).
        x_error : numpy array
            the error in the magnetic field values (in Gauss). Set to [] by default.  
        y_error : numpy array
            the error in the rotation values. Set to [] by default. 

        Returns
        -------
        plotable
            Returns a new plotable object for the specified data.  
        """

        self.x = np.array(x)
        self.y = np.array(y)
        self.laser_wavelength = laser_wavelength
        self.optical_length = optical_length
        self.x_error = np.array(x_error)
        self.y_error = np.array(y_error)

    def get_plotable_subset(self, type, index1, index2=None):

        """
        Creates a plotable object who's data is a subset of an existing plotabale.

        Parameters
        ----------
        self : plotable
            The plotable object being truncated. 
        type : numpy array
            the type of truncation to perform. 
                'before' - creates a new plotable with all data with indeces lower than index1
                'after' - creates a new plotable with all data with indeces higher than index1
                'between' - creates a new plotable with all data between index1 and index2
        index1 : int
            the lower valued index. 
        index2 : int
            the higher valued index. Set to None by default
 
        Returns
        -------
        plotable
            Returns a plotable object containing a truncated set of the original data provided.  
        """

        subset = plotable([],[],self.laser_wavelength, self.optical_length)
        length = self.x.size
        bfields = self.x
        rotations = self.y
        bfield_err = self.x_error
        rotation_err = self.y_error
        
        if (type == "before"):
            #create an array of all values before value1 value
                #INCLUDES value1
            #start index is beginning of array
            start_index = 0
            #stop index will be location of value1 +1
            stop_index = index1 +1
            

        if (type == "after"):
            #create an array of all values after value1 
                #INCLUDES value1
            #start index is location of value 1
            start_index = index1
            #stop index is end of array
            stop_index = length


        if (type =="between"):
            #creates an array of values between value1 and value2
                #INCLUDES value1 and value2
            #start index is location of value1
            start_index = index1
            #stop index is location of value2 plus 1
            stop_index = self.find_in_Bfield_array(index2)+1

        subset.x = bfields[start_index:stop_index]
        subset.y = rotations[start_index:stop_index]
        subset.x_error = bfield_err[start_index:stop_index]
        subset.y_error = rotation_err[start_index:stop_index]
        
        return subset
        
#settings for a plot with raw data scatter, and one fit line
class plotSettings:
    """
    A class used plot manage plot settings for density measurement grapha.  

    ...

    Attributes
    ----------
    title : string
        A string to use as the main title of the graph. 
    xlabel : string
        A string to use as the label for the x axis of the graph. 
    ylabel : string
        A string to use as the label for the y axis of the graph. 
    ymin : float 
        The minimum value for the y axis.
    ymax : float
        The maximum value for the x axis. 
    data_set : DataSet
        The data to be plotted. 
    fit_data : DataSet
        The curve fit generated from the experimental data. 
    chisqd : int
       the chi squared value for the curve fit. Defaults to 0.0 
    equation : string
       A string represensting the equation of the curve the data is fit to. Set to '' by default
    density_value : float
        The density value calculated from curve fit. 
    fit_data2 : DataSet???
        Mystery data field. defaults to an empty array. Can maybe be deleted????

    Methods
    -------
    __init__(self,title, xlabel, ylabel, ymin, ymax,data_set,fit_data, chisqd = 0.0, equation = "", density_value = 0, fit_data2 = []):
        creates a new plotSettings object. 
    """

    def __init__(self,title, xlabel, ylabel, ymin, ymax,data_set,fit_data, chisqd = 0.0, equation = "", density_value = 0, fit_data2 = []):
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.ymin = ymin
        self.ymax = ymax
        self.data_set = data_set
        self.fit_data = fit_data
        self.chisqd = chisqd
        self.equation = equation
        self.density_value = density_value
        self.fit_data2 = fit_data2
