import numpy as np
from scipy.optimize import curve_fit
from .constants import PLANKS_CONSTANT, BOLTZMANN_CONSTANT, LIGHT_SPEED, ELECTRON_MASS, BOHR_MAGNETON, ELECTRON_CHARGE
from .alkali_density_calculation import rb_density_second_order, get_first_order_terms_prefactor, get_second_order_terms_prefactor, get_first_order_terms, get_second_order_terms

h = PLANKS_CONSTANT
k = BOLTZMANN_CONSTANT
c = LIGHT_SPEED
m = ELECTRON_MASS
u = BOHR_MAGNETON
e = ELECTRON_CHARGE

def linear_fit_data(x_vals, y_vals):
    """
    Returns a linear fit, using scipy.optimize's curve fit function, for the specified data. This version of the linear fit does not use the error on the points as all in it's calculations. 
    
    Parameters
    ----------
    x_vals : array
        An array of float values to use as the x values for the fit. 
    y_vals :  array
        An array of float values to use as the y values for the fit. 

    Returns
    -------
    param :  array
        An array of length 2, containing the slope and y-intercept values for the linear fit as floats.
    pcov : array
        A 2x2 array containing the covariance matrix for the fit.   
    """
    # line for fitting
    def line(x, m, b):
        return x*m+b
    param, param_cov = curve_fit(line, x_vals, y_vals)
    return param, param_cov

def linear_fit_data_with_error(x_vals, y_vals, errors):
    """
    Returns a linear fit, using scipy.optimize's curve fit function, for the specified data. This version uses the error on the data points as weighting factors when calculating the linear fit. 
    
    Parameters
    ----------
    x_vals : array
        An array of float values to use as the x values for the fit. 
    y_vals :  array
        An array of float values to use as the y values for the fit. 
    errors: array
        An array of float values to use as the error values on the data points for the fit.

    Returns
    -------
    param :  array
        An array of length 2, containing the slope and y-intercept values for the linear fit as floats.
    pcov : array
        A 2x2 array containing the covariance matrix for the fit.   
    """
    # line for fitting
    def line(x, m, b):
        return x*m+b
    param, param_cov = curve_fit(line, x_vals, y_vals, sigma=errors, absolute_sigma=True)
    return param, param_cov

def get_average_error(error_vals):
    """
    Calculates the average error from an array of error values. 
    
    Parameters
    ----------
    error_vals : array
        An array of error values as floats. 

    Returns
    -------
    avg_err :  float
        The average error for the dataset as determined by adding the error values in quadrature and then dividing by the number of data points in the set. 
    """
    avg_err = 0
    l = len(error_vals)
    for i in range(0,l):
        avg_err = avg_err + error_vals[i]**2
    avg_err = np.sqrt(avg_err)/l
    return avg_err

def get_error_from_covar(p_cov):
    """
    Returns the error in the fit as determined by the covariance matrix. 
    
    Parameters
    ----------
    p_cov : array
        The covariance matrix calculated by the linear by. 

    Returns
    -------
    cov_err :  float
        The error as determined by taking the square root of the covariance matrix term associated with the slope value. 
    """
    cov_err = np.sqrt(p_cov[0][0])
    return cov_err

def meanAbsError(data_set):
    """
    Calculates the mean absolute error for a given dataset. 
    
    Parameters
    ----------
    data_set : array
        The set of data to calculate the MAE for.  

    Returns
    -------
    error :  float
        The error as determined by summing the absolute differences from the average and then dividing by the number of data points . 
    """
    sum = 0
    num_pts = len(data_set)
    avg = np.average(data_set)
    for i in range(num_pts): 
        sum += abs(data_set[i] - avg) 
    error = sum/num_pts
    return error

#Get parabolic fit
def get_parabolic_fit(x_data, y_data, weights):
    """
    Calculates a parabolic fit for a given dataset using numpy's polyfit.  
    
    Parameters
    ----------
    x_data : array
        An array of float values representing the x values of the data to be fit to.   
    y_data : array
        An array of float values representing the y values of the data to be fit to. 
    weights : array
        An array of standard deviations for each data point. This will be used to weight points in the fit. 

    Returns
    -------
    model :  array
        A float array containing the coefficients for the fit. 
    covar : array
        A 3x3 array representing the covariance matrix for the fit. 
    """
    _  = np.polyfit(x=x_data, y=y_data, deg=2, w=1/weights, cov=True)
    model = np.poly1d(_[0])
    covar = _[1]

    return model, covar

def get_extended_xs(x_data, num_points, extension_percent):
    """
    Given a set of x values, extends the range by the specified percentage on each side and returns a numpy linespace for that range. 
    
    Parameters
    ----------
    x_data : array
        An array of float values representing the x values of the data.   
    num_points : int
        The number of points to put in the resulting array.
    extension_percent : float
        The percent to extend the x values on each side.
        
    Returns
    -------
    line :  array
        A float array of length num_points, over the specified range.  
    """
    x_min = np.min(x_data)
    x_min = x_min-np.abs(x_min)*extension_percent
    x_max = np.max(x_data)
    x_max = x_max+x_max*extension_percent
    line = np.linspace(x_min, x_max, num_points) 
    return line

def extract_model_coeffs(model):
    """
    Given a set of x values, extends the range by the specified percentage on each side and returns a numpy linespace for that range. 
    
    Parameters
    ----------
    x_data : array
        An array of float values representing the x values of the data.   
    num_points : int
        The number of points to put in the resulting array.
    extension_percent : float
        The percent to extend the x values on each side.
        
    Returns
    -------
    line :  array
        A float array of length num_points, over the specified range.  
    """
    a = float(model[2])
    b = float(model[1])
    c = float(model[0])
    return a, b, c

def get_density_error_from_parabolic_fit(covariance_matrix):
    """
    Estimates the fit error from the covariance matrix from the the parabolic fit.
    
    Parameters
    ----------
    covariance_matrix : array
        A 3x3 array representing the covariance matrix of the fit.    
        
    Returns
    -------
    alk_err :  float
        The error in the fit.  
    """
    sqrt_diags = np.sqrt(np.diag(covariance_matrix))
    alk_err = sqrt_diags[2]
    return alk_err

def get_parabola_extrema(model):
    """
    Given a model for a parabolic fit, returns the extrema of the parabola. 
    
    Parameters
    ----------
    model : array
        A array containing the coefficients of the parabolic fit.    
        
    Returns
    -------
    min_density_wavelength :  float
        The x value of the extremum.  
    min_density : float
        The y value of the extremum. 
    """
    a, b, c = extract_model_coeffs(model)
    min_density_wavelength = -b/(2*a)
    min_density = a*min_density_wavelength**2+b*min_density_wavelength+c
    return min_density_wavelength, min_density

def get_percent_error(error_val, measured_val):
    """
    Calculates the percent error for a given value.  
    
    Parameters
    ----------
    error_val : float
        The error on the value. 
    measured_val : float
        The value. 
        
    Returns
    -------
    perc_err :  float
        The percent error. 
    
    """
    perc_err = 100*error_val/measured_val
    return perc_err



#error analysis
#SOURCE: http://www.geol.lsu.edu/jlorenzo/geophysics/uncertainties/Uncertaintiespart2.html
#propagate error when multiplying values
def add_in_quadrature(errors):
    err = np.sqrt(np.sum(np.array(errors)**2))#errors must be passed as a numpy array
    return err

def multiplication_error(final, errors, values):
    #error and values need to be numpy arrays
    err = np.sqrt(np.sum((np.array(errors)/np.array(values))**2))*final
    return err

def powers_error(final, powers, errors, values):
    #powers, errors, and values need to be numpy arrays
    temp = np.array(powers)*np.array(errors)
    err = np.sqrt(np.sum(((temp)/np.array(values))**2))*final
    return err

def wl_error(probe_error, probe, resonance_error, resonance):
    #get error from resonance - probe
    errors = np.array([probe_error, resonance_error])
    subtraction = add_in_quadrature(errors)
    # get error in probe beam squared
    power = powers_error(probe**2, [2], [probe_error], [probe])
    #get error in probe^2/(resonance-probe)
    delta = resonance-probe
    result = probe**2/delta
    final_error = multiplication_error(result, [power, subtraction], [probe**2, delta])
    return final_error

def wl_terms_error(probe_error, probe, d1_error, d1, d2_error, d2, T):
    #first term
    d1_term = probe**2/(d1-probe)
    d1_err_temp = wl_error(probe_error, probe, d1_error, d1)
    d1_term_err = powers_error(4*d1_term**2, [2], [d1_err_temp], [d1_term**2])
    d2_term = probe**2/(d2-probe)

    d2_err_temp = wl_error(probe_error, probe, d2_error, d2)
    d2_term_err = powers_error(7*d2_term**2, [2], [d2_err_temp], [d2_term**2])
    mixed_term = d1_term*d2_term
    mixed_term_error = multiplication_error(2*mixed_term, [d1_err_temp, d1_err_temp], [d1_term, d2_term])
    #we have all the errors in th pieces, now we get the total error adding in quadrature
    term1_temp = (1/(3*c**2))*add_in_quadrature([d1_term_err, d2_term_err, mixed_term_error])
    #second term
    term2_temp = (h/(k*T*c))*add_in_quadrature([d1_err_temp, d2_term_err])
    final_error = add_in_quadrature([term1_temp, term2_temp])
    return final_error

def density_error(slope_error, slope, length_error, length, probe_error, probe, d1_error, d1, d2_error, d2, T):
    wl_error = wl_terms_error(probe_error, probe, d1_error, d1, d2_error, d2, T)
    wl_val = get_first_order_terms_prefactor(probe)*get_first_order_terms(d1, d2, probe)+get_second_order_terms_prefactor(probe, T)*get_second_order_terms(d1, d2, probe, False)
    rb_den = rb_density_second_order(d1, d2, length, probe, T, slope) 
    rb_error = multiplication_error(rb_den, [slope_error, length_error, wl_error], [slope, length, wl_val])
    return rb_error