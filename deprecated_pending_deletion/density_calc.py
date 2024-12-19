import numpy as np
from math import log10
import pandas as pd
from scipy.optimize import curve_fit
from .utilities import formatter

######################### CONSTANTS #########################
# TODO: Move to it's own constants file
"""
    Value: Bohr Magneton
    Units: erg/Gauss
"""
mu_b = 9.274E-21

"""
    Value: Charge of an Electron
    Units: cm^(3/2)*g^(1/2)/s
"""
q_electron = 4.8032E-10

"""
    Value: Mass of an Electron
    Units: g
"""
m_electron = 9.1094E-28

"""
    Value: Plank's Constant
    Units: erg*s
"""
h = 6.626176E-27

"""
    Value: Speed of Light
    Units: cm/s
"""
light_speed = 29979245800 

"""
    Value: D1 Transition Resonant Wavelength (Rubidium)
    Units: cm
"""
d1_resonance_lambda = 7.948E-5

"""
    Value: D1 Transition Resonant Frequency (Rubidium)
    Units: Hz
"""
#d1_resonance_f = 3.7719E+14 #Rb87
#d1_resonance_f = 3.7710739E+14 #rb 85 not shifted
d1_resonance_f = light_speed/d1_resonance_lambda #rb 85, cell 309A

"""
    Value: D2 Transition Resonant Wavelength (Rubidium)
    Units: cm
"""
d2_resonance_lambda = 7.800334E-5

"""
    Value: D2 Transition Resonant Frequency (Rubidium)
    Units: Hx
"""
#d2_resonance_f = 3.8420406E+14
#d2_resonance_f = 3.842306E+14 #pressure shifted for cell 309A
d2_resonance_f = light_speed/d2_resonance_lambda #pressure low pressure cell line 314

"""
    Value: Boltzmann Constant
    Units: erg/K
"""
k_b = 1.380649E-16

"""
    Value: Constants in the magnetic field equation for Helmholtz Coils
        Note: THIS IS SPECIFIC TO C. WEAVER'S SETUP (as of 12/16/24)
    Calculated by: B = [(4/5)^(3/2)*4*pi*10^-3]*[IN/R]
    Variables: I is current, N is number of turns of wire in coil and R is radius
"""
b_const = ((4 / 5)**(3/2)) * 4E-3 * np.pi

"""
    Value: Verdet constant of Pyrex Glass at 773nm
        Notes: as reported by Phelps et all in https://doi.org/10.1063/1.4926459
    Units: radians/(cm*Gauss)
"""
verdet_glass = 2.3e-6

"""
    Value: Optical Path Length through our specific cylindrical cells
    Units: cm
"""
glass_depth = 1.3
######################## FUNCTIONS #################################

######################## Alkali Metal Density Functions #####################################
# TODO: MOVE TO OWN file

#rd_density_first_order - only calculates main term of density equation
#rb_density_second_order - includes paramagnetic term (can be additive or subtractive)
#rb_density_third_order - includes paramagnetic term and Romalis Asymetry correction

def get_main_prefactor(optical_length):
    """
    Calculates the overall prefactor for the Alkali Metal Density equation: (e^2*l*mu_b)/(m*h*c) 
    All values are in cgs units.        

    Parameters
    ----------
    optical_length : float
        Path length traveled through the cell by the probe beam. 
        Units: cm

    Returns
    -------
    prefactor : float
        The prefactor for the alkali metal density equation as calculated by (e^2*l*mu_b)/(m*h*c)
    """
    prefactor = (optical_length*q_electron**2*mu_b)/(6*m_electron*light_speed*h)
    return prefactor

def get_first_order_terms_prefactor(probe_beam):
    """
    Calculates the prefactor for the first set of wavelength terms in the Alkali Metal Density equation: (probe_beam)/(3*c^2) 
    All values are in cgs units.        

    Parameters
    ----------
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm

    Returns
    -------
    fo_prefactor : float
        The prefactor for the first term in the alkali metal density equation, as calculated by (probe_beam)/(3*c^2)
    """
    fo_prefactor = probe_beam**2/(3*light_speed**2)
    return fo_prefactor

def get_second_order_terms_prefactor(probe_beam, temp):
    """
    Calculates the prefactor for second set of wavelength terms in the Alkali Metal Density equation: (h)/(k_b*T) 
    All values are in cgs units.        

    Parameters
    ----------
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin)

    Returns
    -------
    so_prefactor : float
        The prefactor for the second term in the alkali metal density equation, as calculated by (h)/(k_b*T)
    """
    T_in_Kelvin = convertTtoKelvin(temp)
    so_prefactor = (h*probe_beam)/(light_speed*k_b*T_in_Kelvin)
    return so_prefactor

def get_first_order_terms(d1_res, d2_res, probe_beam):
    """
    Calculates the first term in the alkali metal density equation. 
    All values are in cgs units.        

    Parameters
    ----------
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm

    Returns
    -------
    fo_terms : float
        The first order term in the alkali metal density equation. 
    """
    d1_term = (4*d1_res**2)/(d1_res-probe_beam)**2
    d2_term = (7*d2_res**2)/(d2_res-probe_beam)**2
    mixed_term = (-2*d1_res*d2_res)/((d1_res-probe_beam)*(d2_res-probe_beam))
    fo_terms = d1_term+d2_term+mixed_term
    return fo_terms

def get_second_order_terms(d1_res, d2_res, probe_beam, isPositive):
    """
    Calculates the first term in the alkali metal density equation. 
    All values are in cgs units.        

    Parameters
    ----------
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    isPositive : boolean
        Indicates whether this value should be a positive or negative correction term. 

    Returns
    -------
    so_terms : float
        The second order term in the alkali metal density equation. 
    """
    d1_term = d1_res/(d1_res-probe_beam)
    d2_term = d2_res/(d2_res-probe_beam)
    if(isPositive==True):
        so_terms = d1_term-d2_term
    else:
        so_terms = -(d1_term-d2_term)
    return so_terms

def get_asymmetry_term(optical_length, oscillator_strength, line_width, kappa, probe_beam, resonance, Td):
    """
    Calculates the asymmetry correction term in the alkali metal density equation. See Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5 for additional information on this term. 
    All values are in cgs units.        

    Parameters
    ----------
    optical_length : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used. 
        Units: cm
    oscillator_str : float
        Oscillator strength for the transition and alkali metal used. 
    line_width : float
        Width of the transition line. 
        Units: Hz
    kappa : float
        A ratio associated with the specific transition being used. 
    Td : float
        The asymmetry parameter. Reported by Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5.
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm

    Returns
    -------
    asymmetry : float
        Returns the asymmetry correction term to the density equation. 
    """
    numerator = 0.106*Td*optical_length*mu_b*oscillator_strength*line_width**2*kappa*resonance**6*q_electron**2
    denominator = m_electron*light_speed**4*h*(probe_beam-resonance)**3
    asym_correction = numerator/denominator
    return asym_correction

#first term in the density equation, no additional corrections
def rb_density_first_order(d1_res, d2_res, optical_length, probe_beam, slope):
    """
    Calculates the alkali metal density. Uses only the terms in Chann et al (2002) DOI: 10.1103/PhysRevA.66.032703, equation 9. 
    All values are in cgs units.        

    Parameters
    ----------
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    optical_length : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    slope : float
        The slope value determined by a linear fit of magnetic field vs. faraday rotation data.  

    Returns
    -------
    rb_density : float
        Returns the alkali metal density. 
    """
    prefactor0 = get_main_prefactor(optical_length)
    prefactor1 = get_first_order_terms_prefactor(probe_beam)
    first_order_terms = get_first_order_terms(d1_res, d2_res, probe_beam)
    F_lambda = prefactor0*(prefactor1*first_order_terms)
    rb_density = slope/F_lambda
    return rb_density
    
#first term in density equation and paragmagnetic correction
def rb_density_second_order(d1_res, d2_res, optical_length, probe_beam, temp, slope):
    """
    Calculates the alkali metal density, including the paramagnetic correction term. See Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5, equation 1, for the approximate form of this equation, though note that Vleigen's first term is incorrect. 
    All values are in cgs units.        

    Parameters
    ----------
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    optical_length : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin) 
    slope : float
        The slope value determined by a linear fit of magnetic field vs. faraday rotation data.  

    Returns
    -------
    rb_density : float
        Returns the alkali metal density, with the paramagnetic correction. 
    """
    prefactor0 = get_main_prefactor(optical_length)
    prefactor1 = get_first_order_terms_prefactor(probe_beam)
    prefactor2 = get_second_order_terms_prefactor(probe_beam, temp)
    fo_terms = get_first_order_terms(d1_res, d2_res, probe_beam)
    so_terms = get_second_order_terms(d1_res, d2_res, probe_beam, False)
    F_lambda = prefactor0*(prefactor1*fo_terms+prefactor2*so_terms)
    rb_density = slope/F_lambda
    return rb_density

#first term in density equation, plus paramagentic correction, plus asymmetry correction
def rb_density_third_order(d1_res, d2_res, optical_length, probe_beam, temp, 
                           oscillator_strength, line_width, kappa, Td, slope):
    """
    Calculates the alkali metal density, including the paramagnetic correction term. See Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5 equations 1 and 3, for the approximate form of this equation, though note that Vleigen's first term is incorrect. 
    All values are in cgs units.        

    Parameters
    ----------
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    optical_length : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    probe_beam : float
        Wavelength of the probe beam used.  
        Units: cm
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin) 
    oscillator_str : float
        Oscillator strength for the transition and alkali metal used. 
    line_width : float
        Width of the transition line. 
        Units: Hz
    kappa : float
        A ratio associated with the specific transition being used. 
    Td : float
        The asymmetry parameter. Reported by Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5.
    slope : float
        The slope value determined by a linear fit of magnetic field vs. faraday rotation data.  

    Returns
    -------
    rb_density : float
        Returns the alkali metal density, with the paramagnetic and asymmetry corrections. 
    """
    prefactor0 = get_main_prefactor(optical_length)
    prefactor1 = get_first_order_terms_prefactor(probe_beam)
    prefactor2 = get_second_order_terms_prefactor(probe_beam, temp)
    fo_terms = get_first_order_terms(d1_res, d2_res, probe_beam)
    so_terms = get_second_order_terms(d1_res, d2_res, probe_beam, False)
    F_lambda = prefactor0*(prefactor1*fo_terms+prefactor2*so_terms)
    F_asym = get_asymmetry_term(optical_length, oscillator_strength, line_width, kappa, probe_beam, d2_res, Td)
    F_all = F_lambda+F_asym
    rb_density = slope/F_all
    return rb_density

##################################################################################################

####################### CONVERSION FUNCTIONS  ################################
# TODO: Move to own file

def get_frequency_from_wavelength(wavelength):
    """
    Converts a wavelength of light to the corresponding frequency value. All units are cgs. 

    Parameters
    ----------
    wavelength : float
        Wavelength to be converted. Wavelength should be entered in cm. 

    Returns
    -------
    freq : float
        The frequency value corresponding to the input wavelength value.  
        Calculated as f = c/λ. 
        Units: Hz
    """
    freq = light_speed/wavelength
    return freq

def convertTtoKelvin(temp):
    """
    Converts a Celsius temperature to Kelvin.

    Parameters
    ----------
    temp : float
        Temperature, in Celsius, to be converted to Kelvin. 

    Returns
    -------
    T : float
        Temperature in Kelvin. 
    """
    T = temp+273.15
    return T

def convertItoB(current):
    """
    Converts the current in a pair Helmholtz coils into the magnetic field present at their center, in Gauss. 
    NOTE: this is for the original coils I used my first summer. 

    Parameters
    ----------
    current : float
        The current measured in the coil wires. 

    Returns
    -------
    b_field : float
        Magnetic field strength in Gauss. 
    """
    num_turns = 110
    radius = 0.21 #meters
    b_field = b_const*float(current)*num_turns/radius
    return b_field

def convertItoB_mainroom_DEPRICATED(current):
    """
    Converts the current in a pair Helmholtz coils into the magnetic field present at their center, in Gauss. 
    This is specifically for C. Weaver's setup. Based on the magnetic field as determined by measuring several B-field values, at currents 0-5amps in 1 amp increments. bfield =  2.081*float(current) - 0.07857 
    NOTE: THIS IS DEPRECATED DO NOT USE. Why haven't I deleted it you ask? I don't know, superstition or whatever. Probably. 

    Parameters
    ----------
    current : float
        The current measured in the coil wires. 

    Returns
    -------
    b_field : float
        Magnetic field strength in Gauss. 
    """
    num_turns = 100
    radius = 0.1905 #meters
    #calculates B from helmholtz coil eqn
    bfield = b_const*float(current)*num_turns/radius
    return bfield

def convertItoB_mainroom(current):
    """
    Converts the current in a pair Helmholtz coils into the magnetic field present at their center, in Gauss. 
    This is specifically for C. Weaver's setup. 
    NOTE: The calculation is based on EPR data obtained from the coils and so is the most accurate version of this function. Use this one for all main room dev. 

    Parameters
    ----------
    current : float
        The current measured in the coil wires. 

    Returns
    -------
    b_field : float
        Magnetic field strength in Gauss. 
    """
    bfield = float(current) * 2.17
    return bfield

def convertVtoRot(voltage, noB_voltage, conversion):
    """
    Converts voltage read by the photodiode into rotation in radians. 

    Parameters
    ----------
    voltage : float
        The voltage reading to convert to rotation. 
    noB_voltage : float
        The voltage reading at zero rotation. 
    conversion : 
        The conversion factor measured during data collection. 

    Returns
    -------
    rotation : float
        The rotation value in radians.  
    """
    deltaV = voltage - noB_voltage
    rotation = deltaV*conversion
    return rotation

def calculateRotationConversionFactor(voltage_diff, cal_rot):
    """
    Calculates the conversion factor for a dataset using the voltage difference and the known angle used for calibration.  

    Parameters
    ----------
    voltage_diff : float
        The voltage difference between the first and second measurements taken during the calibration procedure.   
    cal_rot : 
        The angle rotated by the half-wave plate during calibration.  

    Returns
    -------
    conversion_factor : float
        The conversion factor in radians/Volt  
    """
    cal_rot_Radians = float(cal_rot) * (np.pi/180)
    conversion_factor = cal_rot_Radians/voltage_diff
    return conversion_factor

#sometimes the wavelengths get entered in nm not cm
#convert them when that happens
def convert_to_cm_if_needed(wavelength):
    """
    Converts wavelength values entered into the density data collection app nm into cm. This function assumes that users will either enter the wavelength as cm (the correct units for consistency with cgs system of units) or nm (the more conceptually friendly units for wavelength of the relevant size). So wavelengths entered are checked and if the number entered is greater than 100, it is assumed that the user entered the value in nm, rather than cm and converts to cm accordingly. 

    Parameters
    ----------
    wavelength : float
        The wavelength of the probe beam. 

    Returns
    -------
    converted_wavelength :  float
        The error as determined by taking the square root of the covariance matrix term associated with the slope value. 
    """
    if(wavelength>100):
        converted_wavelength = wavelength*(10**(-7))
    else: 
        converted_wavelength = wavelength
    return converted_wavelength
##################################################################################################


######################### FITTING AND ERROR FUNCTIONS ##########################################
# TODO: move to own file
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

################################################################################################################

############################### DATA FILES AND DATA PROCESSING #####################################################

def get_processed_data_from_csv(fp):
    """
    Returns density data in a csv file as a set of arrays. 
    
    Parameters
    ----------
    fp : string
        The file path to the file containing the target data. 

    Returns
    -------
    magnetic_fields : array 
        An array of float values representing the magnetic field values used in the experiment. 
    rotation_vals : array 
        An array of float values representing the rotation field values found in the experiment. 
    rotation_MAE : array 
        An array of float values representing the mean average error of the rotation values found in the experiment. 
    rotation_STD : array 
        An array of float values representing the standard deviations of the rotation values found in the experiment. 
    """
    processed_data = pd.read_csv(fp)
    # Convert each column of the dataframe into a numpy array
    magnetic_fields = processed_data["Magnetic Field (Gauss)"].to_numpy()
    rotation_vals = processed_data["Rotation (Radians)"].to_numpy()
    rotation_MAE = processed_data["Rotation Mean Absolute Error"].to_numpy()
    rotation_STD = processed_data["Rotation Standard Deviation"].to_numpy()

    return magnetic_fields, rotation_vals, rotation_MAE, rotation_STD

def get_info_from_fname(processed_filepath):
    """
    Takes the file path to a processed faraday rotation data set and returns the experiment parameters associated with that file.
    
    Parameters
    ----------
    processed_filepath : string
        The file path to the file containing the target data. 

    Returns
    -------
    col_date : string 
        The collection date of the experiment. 
    cell_name : string 
        The id of the cell used in the experiment. 
    temperature : string 
        The oven temperature, in Celsius, used for the experiment. 
    """
    #split the file path by / 
    fp_ary = str(processed_filepath).split('/')
    #take the last element of the array to get the file name
    #split that on . to separate extension from rest of name
    properties = fp_ary[-1].split('.')[0].split('_')
    #need to get the following params from the 
    col_date = properties[0]
    cell_name = properties[1].split('-')[1]
    temperature = properties[2].split('-')[1]
    return col_date, cell_name, temperature

#TODO - rename this function
def get_my_data_no_file(date, cellname, temp, data, d1_res, d2_res, wavelength, optical_path, isPositive, verdet_adjustment):
    """
    Calculates the alkali metal density, including the paramagnetic correction term. See Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5 equations 1 and 3, for the approximate form of this equation, though note that Vleigen's first term is incorrect. 
    All values are in cgs units.        

    Parameters
    ----------
    date : string
        The date on which the experiment was performed. 
    cell_name : string 
        The ID of the cell used for the experiment. 
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin) 
    data : 
        A DataFrame object containing the magnetic field, rotation, and rotation standard deviation data. 
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    wavelength : float
        Wavelength of the probe beam used.  
        Units: cm
    optical_path : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    isPositive :  boolean   
        A boolean value indicating whether the paramagnetic correction term should be positive or negative. 
    verdet_adjustment : float
        The value used to adjust the rotation data to account for the Verdet effect. 

    Returns
    -------
    output : DataFrame
        A DataFrame containing the experimental data formatted for further analysis. 
    """

    collected_date = date
    cell = cellname
    tmp = float(temp)
    b_field = data["Magnetic Field (Gauss)"]
    rot = data["Rotation (Radians)"]
    r_err_STD = data["Rotation Standard Deviation"]
    wl_err = 3E-10
    f = .667 #ocillator strength
    k = 7/6 #kappa
    line_wid = 3e9 #line width (Hz)
    T_d = 34e-13 #T_d from romalis (s)

    #get density without verdet adjustment
    fit_params_0, cov_0 = linear_fit_data_with_error(b_field, rot, r_err_STD)
    slope_0 = fit_params_0[0]
    cov_err_0 = get_error_from_covar(cov_0)
    uncorrected_density = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, slope_0)
    uncorrected_density_err = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, cov_err_0)

    #adjust rotations using verdet constant of glass
    rot_adj = glass_verdet_adj(verdet_adjustment, rot, b_field)

    fit_params, cov = linear_fit_data_with_error(b_field, rot_adj,r_err_STD)
    slope = fit_params[0]
    cov_err = get_error_from_covar(cov)

    FO_density = rb_density_first_order(d1_res, d2_res, optical_path, wavelength, slope)
    FO_density_error = rb_density_first_order(d1_res, d2_res, optical_path, wavelength, cov_err)
    SO_density = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, slope)
    SO_density_error = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, cov_err)
    TO_density = rb_density_third_order(d1_res, d2_res, optical_path, wavelength, tmp, f, line_wid, k, T_d, slope)
    TO_density_error = rb_density_third_order(d1_res, d2_res, optical_path, wavelength, tmp, f, line_wid, k, T_d, cov_err)
    ### KILLIAN DENSITY
    killian_val = formatter(killian_density(tmp),4)

    #create my data frame
    output = pd.DataFrame({'Date': [collected_date],
                        'Cell Name': [cell],
                        'Temperature':[tmp],
                        'Uncorrected Density': [formatter(uncorrected_density,6)],
                        'Uncorrected Density Error': [formatter(uncorrected_density_err,6)],
                        'First Order Density':[formatter(FO_density, 6)],
                        'FO Density Error':[formatter(FO_density_error, 6)],
                        'Second Order Density': [formatter(SO_density, 6)],
                        'SO Density Error': [formatter(SO_density_error, 6)],
                        'Third Order Density': [formatter(TO_density, 6)],
                        'TO Density Error': [formatter(TO_density_error, 6)],
                        'Killian Value':[killian_val],
                        'D1 Resonance':[formatter(d1_res,5)],
                        'D2 Resonance':[formatter(d2_res,5)],
                        'Probe Beam':[formatter(wavelength, 5)]})
    return output

##################################################################################################

####################### MISC. #####################################################################

def glass_verdet_adj(verdet_rotation, rotations, mag_fields):
    """
    Adjusts the rotation values to account for the Verdet effect of the cell glass and oven windows.  

    Parameters
    ----------
    verdet_rotation : float
        Verdet effect constant for the experiment. 
        Units: radians/cm*Gauss
    rotations : array
        An array containing the uncorrected rotation values as floats.  
    mag_fields: array 
        An array containing the magnetic field values as floats. 

    Returns
    -------
    adjusted_rotations : array
        An array of rotation values adjusted to account for the Verdet effect, as floats. 
    """
    adjusted_rotations = []
    for i in range(0,len(mag_fields)):
        verdet_adjment = verdet_rotation*mag_fields[i]
        adjusted_rot = rotations[i]-verdet_adjment
        adjusted_rotations.append(adjusted_rot)
    return adjusted_rotations

def killian_density(temp):
    """
    Calculates the Killian Density Values for the specified oven temperature. See Killian (1926) 10.1103/PhysRev.27.578 for additional information. 
    NOTE: This function calculates the Killian density for Rb specifically. 

    Parameters
    ----------
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin)  

    Returns
    -------
    rb_den : float 
        The density of Rubidium as calculated by Killian's empirical equation. 
    """
    T = convertTtoKelvin(temp)
    a=26.41
    b=4132/T
    c = log10(T)
    rb_den = 10 **(a-b-c)
    return rb_den