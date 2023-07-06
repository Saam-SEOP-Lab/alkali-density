import numpy as np

#class for storing a data set to be plotted on an x y scatter plot
class plotable:
    
    def __init__(self, x, y, laser_wavelength, optical_length, x_error = [], y_error = []):
        self.x = np.array(x)
        self.y = np.array(y)
        self.laser_wavelength = laser_wavelength
        self.optical_length = optical_length
        self.x_error = np.array(x_error)
        self.y_error = np.array(y_error)

    def get_plotable_subset(self, type, index1, index2=None):
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
