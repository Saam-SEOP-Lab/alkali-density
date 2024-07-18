import numpy as np
from scipy.optimize import curve_fit
import CurveFit as cfit
import plotSettings as ps
import Functions as f
import Utilities as util
import densityCalculations as calc

#DataSet takes two arrays, one for the x coordinates and one for the y coorinates 
#of a data set
class DataSet:
    #constructor
    # a data set has an array of x coordinates, 
    # an array of y coordinates 
    # and a function to fit them to
    def __init__(self, plotdata, function, ftype, samples):
        self.plotdata = plotdata
        self.function = function
        self.fit = self.fit_to_curve(function)
        self.fitted_data = self.get_fit_line(samples, ftype)
        self.chisqd = self.get_chi_squared_linefit()
        self.equation = self.get_equation_linear()
        self.standard_deviation = self.getStdDev()

    
    #this takes the function provided when the data set is constructed 
    # and creates a curve fit from it. 
    # this curve fit is stored in the DataSet and can be accessed via dataset.fit
    def fit_to_curve(self, function):
        x_data = self.plotdata.x
        y_data = self.plotdata.y
        error_in_y = self.plotdata.y_error
        param, pcov = curve_fit(function, x_data, y_data, sigma=error_in_y, absolute_sigma=True)
        fit = cfit.CurveFit(param, pcov)
        return fit
    
    def getPcov(self):
        pcov = self.fit.cov
        return pcov

    def getStdDev(self):
        pcov = self.getPcov()
        error = np.sqrt(np.diag(pcov))
        return error


    def getParam(self):
        param = self.fit.coeff
        return param

    # for data that has been fit to a line, this returns the equation as a nicely formatted string
    def get_equation_linear(self):
        lf = self.fit
        a = lf.coeff[0] #slope
        b = lf.coeff[1] #y-intercept
        equation = 'y = ' + util.formatter(a, 2) +'x + ' + util.formatter(b, 2)
        return equation
    
    # I think I want to create the curve fit to plot and store that on the data set as well
    # I also want to eventually expand this to be able to handle more than just lines
    # current options for ftype: 'line', 'nlog'
    def get_fit_line(self, num_samples, ftype):
        x_fitted = np.linspace(np.min(self.plotdata.x), np.max(self.plotdata.x), num_samples)
        if ftype == 'line':
            y_fitted = self.fit.coeff[0] * x_fitted + self.fit.coeff[1]
        if ftype == 'nlog':
            y_fitted = self.fit.coeff[0] * np.log(np.abs(self.fit.coeff[1] * x_fitted)) + self.fit.coeff[2]
        fitted_data = ps.plotable(x_fitted,y_fitted, self.plotdata.laser_wavelength, self.plotdata.optical_length)
        return fitted_data


    #gets chi squared value from the curve fit and data provided
    # currently only works for lines    
    def get_chi_squared_linefit(self):
        x_data = self.plotdata.x
        y_data = self.plotdata.y
        y_err = self.plotdata.y_error
        coef = self.fit.coeff
        model = f.line(x_data, coef[0], coef[1])
        chisq = sum(((y_data-model)/y_err)**2)
        return chisq
    
    #helper function to find the index of the specified value
    #used in data_subset_bfield
    def find_in_Bfield_array(self, value):
        bfield = self.plotdata.x
        #find the first index where value exists in the bfield array
        #note that I am assuming that there will be no (or at least minimal) repeated values
        location = np.where(bfield==value)[0][0]
        return location

    #create a data set object with all values either above or below the specified B field value
    #type options are "before", "after", "from"
    def data_subset_bfield(self, type, value1, value2=None):
        subset = ps.plotable([],[],self.plotdata.laser_wavelength, self.plotdata.optical_length)
        length = self.plotdata.x.size
        bfields = self.plotdata.x
        rotations = self.plotdata.y
        bfield_err = self.plotdata.x_error
        rotation_err = self.plotdata.y_error
        value1_loc = self.find_in_Bfield_array(value1)

        if (type == "before"):
            #create an array of all values before value1 value
                #INCLUDES value1
            #start index is beginning of array
            start_index = 0
            #stop index will be location of value1 +1
            stop_index = value1_loc +1
            

        if (type == "after"):
            #create an array of all values after value1 
                #INCLUDES value1
            #start index is location of value 1
            start_index = value1_loc
            #stop index is end of array
            stop_index = length-1


        if (type =="between"):
            #creates an array of values between value1 and value2
                #INCLUDES value1 and value2
            #start index is location of value1
            start_index = value1_loc
            #stop index is location of value2 plus 1
            stop_index = self.find_in_Bfield_array(value2)+1

        subset.x = bfields[start_index:stop_index]
        subset.y = rotations[start_index:stop_index]
        subset.x_error = bfield_err[start_index:stop_index]
        subset.y_error = rotation_err[start_index:stop_index]
        
        return subset
    
    #create a data set object with all values either above or below the specified B field value
    #type options are "before", "after", "from"
    def data_subset_index(self, type, index1, index2=None):
        subset = ps.plotable([],[],self.plotdata.laser_wavelength, self.plotdata.optical_length)
        length = self.plotdata.x.size
        bfields = self.plotdata.x
        rotations = self.plotdata.y
        bfield_err = self.plotdata.x_error
        rotation_err = self.plotdata.y_error
        
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


    def calculate_rb_density(self):
        slope = self.fit.coeff[0]
        wavelength = self.plotdata.laser_wavelength
        optical_path = self.plotdata.optical_length
        err = np.average(self.get_y_error_vals())
        density = abs(calc.rb_density(slope,optical_path, wavelength))
        err = abs(calc.rb_density(err, optical_path, wavelength))
        #print(err)
        return density, err


    def rb_density_formatted(self):
        den, err = self.calculate_rb_density()
        #units = " cm^-3"
        formatted_density = util.formatter(den, 2)
        formatted_err = util.formatter(err, 0)
        return formatted_density, formatted_err

    def get_y_error_vals(self):
        y_error = self.plotdata.y_error
        return y_error
    
    def get_y_vals(self):
        y_vals = self.plotdata.y
        return y_vals
    
    def get_x_vals(self):
        x_vals = self.plotdata.x
        return x_vals