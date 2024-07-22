import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import plotSettings as ps



def Line(x, a, b):
    y = a*x + b
    return y

def fit_to_line(data_to_fit):
    param, pcov = curve_fit(Line, data_to_fit.x, data_to_fit.y)
    linear_fit = [param, pcov]
    return linear_fit

def get_equation_linear(linear_fit):
    param = linear_fit[0]
    a = param[0] #slope
    b = param[1] #y-intercept
    equation = 'y = ' + str(a) +'x + ' + str(b)
    return equation

#functions for creating a plot with fit lines other than mx+b 
def fit_to_ln(data_to_fit):
    # Fit the function a * np.log(b * t) + c to x and y
    param, pcov = curve_fit(lambda t, a, b, c: a * np.log(np.abs(b * t)) + c, data_to_fit.x, data_to_fit.y)
    log_fit = [param, pcov]
    return log_fit

def fit_to_sine(data_to_fit):
    # Fit the function a * np.sin(b * t) + c to x and y
    param, pcov = curve_fit(lambda t, a, b, c: a * np.sin(b * t) + c, data_to_fit.x, data_to_fit.y)
    sine_fit = [param, pcov]
    return sine_fit

def Gaussian(x, a, b, c, d):
    gauss = a * np.exp((x-b) ** 2 / c) + d
    return gauss

def fit_to_gaussian(data_to_fit):
    param, pcov = curve_fit(Gaussian, data_to_fit.x, data_to_fit.y)
    gaussian_fit = [param, pcov]
    return gaussian_fit

def get_equation_ln(log_fit):
    param = log_fit[0]
    a = param[0]
    b = param[1]
    c = param[2]
    equation = 'y = (' + str(a) + ')*ln(' + str(b) +'x)+' + str(c)
    return equation

#set up the curves for fitting
def make_it_fit_line(raw_data_line, linear_fit):
    x_fitted_line = np.linspace(np.min(raw_data_line.x), np.max(raw_data_line.x), 100)
    y_fitted_line = linear_fit[0][0] * x_fitted_line + linear_fit[0][1]
    fitted_data_line = ps.plotable(x_fitted_line,y_fitted_line)
    return fitted_data_line


def make_it_fit_log(raw_data_ln, log_fit):
    x_fitted_ln = np.linspace(np.min(raw_data_ln.x), np.max(raw_data_ln.x), 100)
    y_fitted_ln = log_fit[0][0] * np.log(np.abs(log_fit[0][1] * x_fitted_ln)) + log_fit[0][2]
    fitted_data_ln = ps.plotable(x_fitted_ln,y_fitted_ln)
    return fitted_data_ln
    
    
#gets covariances for anything using curvefit to fit curves
def get_covariences(the_fit):
    pcov = the_fit[1]
    return pcov

def get_param_std(pcov):
    perr = np.sqrt(np.diag(pcov))
    return perr

def better_plot(settings):
    # Plot
    ax = plt.axes()
    #ax.scatter(settings.data_set.x, settings.data_set.y, label='Raw data')
    ax.errorbar(settings.data_set.x, settings.data_set.y,settings.data_set.y_error, fmt='b.', label='Raw data')
    ax.plot(settings.fit_data.x, settings.fit_data.y, 'black', label='Fitted curve')
    #display chi-squared and equation on plot
    plt.figtext(0.15, 0.75, "Equation: "+ settings.equation +"\nDensity: "+ settings.density_value, fontweight = "bold")

    #display grid lines
    ax.minorticks_on()
    ax.grid(which= 'major', color = 'green', linestyle = '--', linewidth = '1.0')
    ax.grid(which= 'minor', linestyle=':', linewidth='0.5', color='black')
    ax.set_title(settings.title)
    ax.set_ylabel(settings.ylabel)
    ax.set_ylim(settings.ymin, settings.ymax )
    ax.set_xlabel(settings.xlabel)
    ax.legend()

def even_better_plot(settings):
    # Plot
    ax = plt.axes()
    ax.scatter(settings.raw_data1.x, settings.raw_data1.y, color='black', label='Raw data')
    ax.plot(settings.fit_data1.x, settings.fit_data1.y, 'blue', label='Fitted curve1')
    ax.plot(settings.fit_data2.x, settings.fit_data2.y, 'orange', label='Fitted curve2')
    #display grid lines
    ax.minorticks_on()
    ax.grid(which= 'major', color = 'green', linestyle = '--', linewidth = '1.0')
    ax.grid(which= 'minor', linestyle=':', linewidth='0.5', color='black')
    ax.set_title(settings.title)
    ax.set_ylabel(settings.ylabel)
    ax.set_ylim(settings.ymin, settings.ymax )
    ax.set_xlabel(settings.xlabel)
    ax.legend()

#like the other plots but just makes a nice scatter plot, no fits
def basic_plot(settings):
    # Plot
    ax = plt.axes()
    ax.scatter(settings.data_set.x, settings.data_set.y, label='Raw data')
    #display grid lines
    ax.minorticks_on()
    ax.grid(which= 'major', color = 'green', linestyle = '--', linewidth = '1.0')
    ax.grid(which= 'minor', linestyle=':', linewidth='0.5', color='black')
    ax.set_title(settings.title)
    ax.set_ylabel(settings.ylabel)
    ax.set_ylim(settings.ymin, settings.ymax )
    ax.set_xlabel(settings.xlabel)
    ax.legend()
    
#like the other plots but just makes a nice scatter plot, no fits
def basic_plot(x, y):
    # Plot    
    ax = plt.axes()
    ax.scatter(x, y, label='Raw data')
    #display grid lines
    ax.minorticks_on()
    ax.grid(which= 'major', color = 'green', linestyle = '--', linewidth = '1.0')
    ax.grid(which= 'minor', linestyle=':', linewidth='0.5', color='black')
    #ax.set_title(settings.title)
    #ax.set_ylabel(settings.ylabel)
    ax.set_ylim(y.min(), y.max())
    #ax.set_xlabel(settings.xlabel)
    ax.legend()