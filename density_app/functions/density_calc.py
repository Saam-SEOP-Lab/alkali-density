import numpy as np
from typing import Type
from math import log10
import pandas as pd
from scipy.optimize import curve_fit
from .utilities import formatter


######################### CONSTANTS #########################

#bohr magneton value
#units: erg/Gauss
mu_b = 9.274E-21

#electron charge
#units: cm^3/2*g^1/2 / s
q_electron = 4.8032E-10

#electron mass
#units: g
m_electron = 9.1094E-28

#planks constant
#units: erg*s
h = 6.626176E-27

#speed of light 
#units: cm/s
light_speed = 29979245800 

#D1 transition resonance wavelength
#units: cm
d1_resonance_lambda = 7.948E-5

#D1 transition resonance frequency
#units: Hz
#d1_resonance_f = 3.7719E+14 #Rb87
#d1_resonance_f = 3.7710739E+14 #rb 85 not shifted
d1_resonance_f = light_speed/d1_resonance_lambda #rb 85, cell 309A


#D2 transition resonance wavelength
#units: cm
d2_resonance_lambda = 7.800334E-5

#D2 transition resonance frequency
#units: Hz
#d2_resonance_f = 3.8420406E+14
#d2_resonance_f = 3.842306E+14 #pressure shifted for cell 309A
d2_resonance_f = light_speed/d2_resonance_lambda #pressure low pressure cell line 314

#Boltzman Constant
#erg/K
k_b = 1.380649E-16

#constants in the B field equation for helmholz coils
#B = [(4/5)^(3/2)*4*pi*10^-3]*[IN/R]
#I is current, N is number of turns of wire in coil and R is radius
#this is for the coils used in the front room set up
b_const = ((4 / 5)**(3/2)) * 4E-3 * np.pi

#verdet constand of Pyrex Glass at 773nm, in radians/cm*Gauss
verdet_glass = 2.3e-6

#glass depth for cylindrical cells
glass_depth = 1.3
######################## FUNCTIONS #################################

#given the laser frequency, returns the difference from given resonance
# ∆ = f_probe - f_resonance
#units: cgs
def get_Delta_D(transition_freq, laser_freq):
    delta_D =  laser_freq - transition_freq
    return delta_D

#given laser wavelength, returns laser frequency
# f = c/λ
#units: cgs
def get_frequency_from_wavelength(wavelength):
    freq = light_speed/wavelength
    return freq

#given laser wavelength, return the delta term in the density calculation
# ∆ = ((∆_D1)^2 (∆_D2)^2)/((4*∆_D2^2)+(*7∆_D1^2)-(2*∆_D2*∆_D1))
def delta_term(d1_res, d2_res, laser_wavelen):
    laser_fr = get_frequency_from_wavelength(laser_wavelen)
    d1_f = get_frequency_from_wavelength(d1_res)
    d2_f = get_frequency_from_wavelength(d2_res)
    D1 = get_Delta_D(d1_f, laser_fr)
    D1_sq = D1**2
    D2 = get_Delta_D(d2_f, laser_fr)
    D2_sq = D2**2
    delta_numerator = D1_sq * D2_sq
    delta_denominator = (4 * D2_sq) + (7 * D1_sq) - (2 * D1 * D2)
    delta_term = delta_numerator/delta_denominator
    return delta_term

#given optical path length return optical path term in density caculation
# F = (18*m_e*h*c)/(l*q_e^2*μ_B)
# (F is for preFactor)
def optical_length_term(o_len):
    ol_numerator = 18 * m_electron * h * light_speed
    ol_denominator = o_len * q_electron**2 * mu_b
    ol = ol_numerator/ol_denominator
    return ol

#converts a temperature in Celcius to Kelvin
def convertTtoKelvin(temp):
    T = temp+273.15
    return T


#given the slope of the rotation vs magnetic field graph, the optical path length 
#and the laser wavelength, return the density of rubidium in the cell
# [Rb] = (θ/B)((18*m_e*h*c)/(l*q_e^2*μ_B))*((∆_D1)^2 (∆_D2)^2)/((4*∆_D2^2)+(*7∆_D1^2)-(2*∆_D2*∆_D1))
def rb_density(d1_res, d2_res, slope, o_len, laser_wave):
    deltas_term = delta_term(d1_res, d2_res, laser_wave)
    opt_len_term = optical_length_term(o_len)
    density = slope * opt_len_term * deltas_term
    return density

#given the slope of the rotation vs magnetic field graph, the optical path length 
#and the laser wavelength, return the density of rubidium in the cell
#accounts for paramagnetic term
# [Rb] = absolutely fuck this equation OMG
## TODO - make a frequency object 
def rb_density_full(d1_res, d2_res, slope, o_len, laser_wave, temp, isPositive):
    fr_D1 = get_frequency_from_wavelength(d1_res)
    fr_D2 = get_frequency_from_wavelength(d2_res)
    f_probe = get_frequency_from_wavelength(laser_wave)
    D1 = get_Delta_D(fr_D1, f_probe) #f_probe - f_D1
    D2 = get_Delta_D(fr_D2, f_probe) #f_probe - f_D2
    T = convertTtoKelvin(temp) 
    prefactor = (6*m_electron*h*light_speed)/(o_len*mu_b*q_electron**2)
    numerator = 3*(D1**2)*(D2**2)*k_b*T
    denominator_main = k_b*T*(4*(D2**2)+7*(D1**2)-2*D1*D2)
    denominator_para = 3*h*D1*D2*(D2-D1)
    if(isPositive==False):
        denominator_para = denominator_para*(-1)
    density = slope*prefactor*numerator/(denominator_main+denominator_para)
    if(isPositive == "both"):
        if(f_probe < fr_D2):
            denominator_para = denominator_para*(-1)

    return density


def rb_density_full_alt(d1_res, d2_res, slope, o_len, laser_wave, temp, isPositive):
    fr_D1 = get_frequency_from_wavelength(d1_res)
    fr_D2 = get_frequency_from_wavelength(d2_res)
    f_probe = get_frequency_from_wavelength(laser_wave)
    D1 = get_Delta_D(fr_D1, f_probe) #f_probe - f_D1
    D2 = get_Delta_D(fr_D2, f_probe) #f_probe - f_D2
    T = convertTtoKelvin(temp) 
    delta_main = (1/3)*(4/(D1**2)+7/(D2**2)-2/(D1*D2))
    delta_para = (h/(k_b*T))*((1/D1)-(1/D2))
    if(isPositive==False):
        delta_para = (-1)*delta_para
    full_delta = delta_main+delta_para
    prefactor = (mu_b*o_len*q_electron**2)/(6*h*m_electron*light_speed)
    density = slope/(prefactor*full_delta)
    return density

def rb_density_full_wavelength(d1_res, d2_res, slope, o_len, laser_wave, temp):
    prefactor = (mu_b*o_len*q_electron**2)/(6*m_electron*h*light_speed)
    delta_wl_d1 = d1_res-laser_wave
    delta_wl_d2 = d2_res-laser_wave
    T = convertTtoKelvin(temp)
    term1 = (laser_wave**2/(3*light_speed**2))*((4*d1_res**2)/delta_wl_d1**2+(7*d2_res**2)/delta_wl_d2**2-(2*d1_res*d2_res)/(delta_wl_d2*delta_wl_d1))
    term2 = (h*laser_wave/(k_b*T*light_speed))*(d1_res/delta_wl_d1 - d2_res/delta_wl_d2)
    combined = prefactor*(term1 - term2)
    density = slope/combined
    return density


#given a current value, number of coil turns, and radius of coil,
#returns the strength of the magnetic field, in Gauss
#for original helmholtz coils
def convertItoB(current):
    num_turns = 110
    radius = 0.21 #meters
    b_field = b_const*float(current)*num_turns/radius
    return b_field

#this is to get the magnetic field for the mainroom set up
def convertItoB_mainroom_DEPRICATED(current):
    num_turns = 100
    radius = 0.1905 #meters
    #based on the magnetic field as determined by measuring several B-field values 
    #at currents 0-5amps in 1 amp increments
    #bfield =  2.081*float(current) - 0.07857 

    #calculates B from helmholtz coil eqn
    bfield = b_const*float(current)*num_turns/radius
    return bfield

#this is to get the magnetic field for the mainroom set up
#based on EPR data
def convertItoB_mainroom(current):
    bfield = float(current) * 2.17
    return bfield

#given a voltage readout, the voltage at 0 field, and a conversion factor,
#returns the rotation value in radians
def convertVtoRot(voltage, noB_voltage, conversion):
    deltaV = voltage - noB_voltage
    rotation = deltaV*conversion
    return rotation

#given 
# the voltage difference between inital and final readings (in Volts)
# the rotation value (in degrees, should be ~.4 degrees typically)
# returns an array containing the conversion factor in radians
def calculateRotationConversionFactor(voltage_diff, cal_rot):
    cal_rot_Radians = float(cal_rot) * (np.pi/180)
    conversion_factor = cal_rot_Radians/voltage_diff
    return conversion_factor

#removes the rotation caused by the verdet constant of the glass in the cell
# verdet constant should be in units of radians/cm*Tesla
# glass_depth should be in units of cm
# mag_field should be in units of Gauss
def glass_verdet_adj(verdet, glass_depth, rotations, mag_fields):
    adjusted_rotations = []
    for i in range(0,len(mag_fields)):
        verdet_adjment = (verdet*glass_depth)*mag_fields[i]
        adjusted_rot = rotations[i]-verdet_adjment
        adjusted_rotations.append(adjusted_rot)
    return adjusted_rotations

# takes a temp in Celcuis and returns the Killian estimated density value of Rb
#comes from Clausius - Klaparone equation
def killian_density(temp):
    T = convertTtoKelvin(temp)
    a=26.41
    b=4132/T
    c = log10(T)
    rb_den = 10 **(a-b-c)
    return rb_den

# gets the data from a processed faraday rotation file 
# returns 4 arrays, one for each column of data in the csv
def get_processed_data_from_csv(fp):
    processed_data = pd.read_csv(fp)
    # Convert each column of the dataframe into a numpy array
    magnetic_fields = processed_data["Magnetic Field (Gauss)"].to_numpy()
    rotation_vals = processed_data["Rotation (Radians)"].to_numpy()
    rotation_MAE = processed_data["Rotation Mean Absolute Error"].to_numpy()
    rotation_STD = processed_data["Rotation Standard Deviation"].to_numpy()

    return magnetic_fields, rotation_vals, rotation_MAE, rotation_STD

#takes the file path to a processed faraday rotation data set and returns the 
#experiment parameters associated with that file
def get_info_from_fname(processed_filepath):
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

#returns a linear fit for the specified data
def linear_fit_data(x_vals, y_vals):
    # line for fitting
    def line(x, m, b):
        return x*m+b
    param, param_cov = curve_fit(line, x_vals, y_vals)
    return param, param_cov

#returns a linear fit for the specified data
def linear_fit_data_with_error(x_vals, y_vals, errors):
    # line for fitting
    def line(x, m, b):
        return x*m+b
    param, param_cov = curve_fit(line, x_vals, y_vals, sigma=errors, absolute_sigma=True)
    return param, param_cov

#calculate average error from errors on individual measurements
def get_average_error(error_vals):
    avg_err = 0
    l = len(error_vals)
    for i in range(0,l):
        avg_err = avg_err + error_vals[i]**2
    avg_err = np.sqrt(avg_err)/l
    return avg_err

#calculate error from covariance matrix from fit
def get_error_from_covar(p_cov):
    cov_err = np.sqrt(p_cov[0][0])
    return cov_err

#given some file path, create a PANDAS series in the form
# [date, cell, temp, density, error]
def get_my_data(d1_res, d2_res, fp, wavelength, optical_path):

    # NOW USES ERROR IN LINE FIT
    # REPORTS ERROR FROM LINE FIT AS DENSITY ERROR

    collected_date, cell, tmp = get_info_from_fname(fp)
    b_field, rot, r_err_MAE, r_err_SDT = get_processed_data_from_csv(fp)
    fit_params, cov = linear_fit_data_with_error(b_field, rot,r_err_SDT)
    slope = fit_params[0]
    #mae_avg_err = get_average_error(r_err_MAE)
    #std_avg_err = get_average_error(r_err_SDT)
    
    den_error = get_error_from_covar(cov)
    ## ERROR NEEDS TO INCLUDE ERROR IN DETUNING - USE CODE BELOW
    # qd_slope = (cov[0][0]/slope)**2
    # qd_detuning = (error_in_detuning/(abs(d2_res-wavelength)))**2 
    # den_error = np.sqrt(sq_slope+qd_detuning)


    #max_err = np.array([mae_avg_err, std_avg_err, cov_err]).max()
    density = formatter(rb_density(d1_res, d2_res, slope, optical_path, wavelength),4)
    density_error = formatter(rb_density(d1_res, d2_res, den_error, optical_path, wavelength),4)
    killian_val = formatter(killian_density(tmp),4)
    #create my data frame
    output = pd.DataFrame({'Date': [collected_date],
                        'Cell Name': [cell],
                        'Temperature':[tmp],
                        'Density':[density],
                        'Density Error':[density_error], 
                        'Killian Value':[killian_val],
                        'D1 Resonance':[formatter(d1_res,5)],
                        'D2 Resonance':[formatter(d2_res,5)],
                        'Probe Beam':[formatter(wavelength, 7)] })
    return output

def get_my_data_no_file(date, cellname, temp, data, d1_res, d2_res, wavelength, optical_path, isPositive):

    #collected_date, cell, tmp = get_info_from_fname(fp)
    #b_field, rot, r_err_MAE, r_err_SDT = get_processed_data_from_csv(fp)

    collected_date = date
    cell = cellname
    tmp = float(temp)
    b_field = data["Magnetic Field (Gauss)"]
    rot = data["Rotation (Radians)"]
    r_err_STD = data["Rotation Standard Deviation"]

    #adjust rotations using verdet constant of glass
    rot_adj = glass_verdet_adj(verdet_glass, glass_depth, rot, b_field)

    fit_params, cov = linear_fit_data_with_error(b_field, rot_adj,r_err_STD)
    slope = fit_params[0]
    cov_err = get_error_from_covar(cov)

    # since we want to compare the density accounting for and not accounting for the paramagnetic term
    # let's calculate and display both I guess
    
    ### DENSITY NO PARAMAGNETIC TERM
    density = formatter(rb_density(d1_res, d2_res, slope, optical_path, wavelength),4)
    density_error = formatter(rb_density(d1_res, d2_res, cov_err, optical_path, wavelength),4)


    ### DENSITY WITH PARAMAGNETIC TERM
    density_raw = rb_density_full(d1_res, d2_res, slope, optical_path, wavelength, tmp, isPositive)
    density_full = formatter(density_raw, 4)
    density_error_full = formatter((rb_density_full(d1_res, d2_res, cov_err, optical_path, wavelength, tmp, isPositive=False)), 4)
    density_raw2 = rb_density_full_alt(d1_res, d2_res, slope, optical_path, wavelength, tmp, isPositive)
    density_full2 = formatter(density_raw2, 4)
    check_diff = formatter(abs(density_raw-density_raw2),4)

    ### KILLIAN DENSITY
    killian_val = formatter(killian_density(tmp),4)

    #create my data frame
    output = pd.DataFrame({'Date': [collected_date],
                        'Cell Name': [cell],
                        'Temperature':[tmp],
                        'Density':[density],
                        'Density Error':[density_error],
                        'Density (with Paramagentic term)': [density_full],
                        'Density (with para sanity check)': [density_full2],
                        '[Rb]_para1-[Rb]_para2': [check_diff],
                        'Density Error (with Paramagentic term)': [density_error_full],
                        'Killian Value':[killian_val],
                        'D1 Resonance':[formatter(d1_res,5)],
                        'D2 Resonance':[formatter(d2_res,5)],
                        'Probe Beam':[formatter(wavelength, 5)] })
    return output

#sometimes the wavelengths get entered in nm not cm
#convert them when that happens
def convert_to_cm_if_needed(wavelength):
    if(wavelength>100):
        converted_wavelength = wavelength*(10**(-7))
    else: 
        converted_wavelength = wavelength
    return converted_wavelength



def get_my_data_compare_to_wleqn(date, cellname, temp, data, d1_res, d2_res, wavelength, optical_path, isPositive):

    #collected_date, cell, tmp = get_info_from_fname(fp)
    #b_field, rot, r_err_MAE, r_err_SDT = get_processed_data_from_csv(fp)

    collected_date = date
    cell = cellname
    tmp = float(temp)
    b_field = data["Magnetic Field (Gauss)"]
    rot = data["Rotation (Radians)"]
    r_err_STD = data["Rotation Standard Deviation"]

    #adjust rotations using verdet constant of glass
    rot_adj = glass_verdet_adj(verdet_glass, glass_depth, rot, b_field)

    fit_params, cov = linear_fit_data_with_error(b_field, rot_adj,r_err_STD)
    slope = fit_params[0]
    cov_err = get_error_from_covar(cov)

    ### DENSITY WITH PARAMAGNETIC TERM
    density_raw = rb_density_full_alt(d1_res, d2_res, slope, optical_path, wavelength, tmp, isPositive)
    density_full = formatter(density_raw, 4)
    density_error_full = formatter((rb_density_full(d1_res, d2_res, cov_err, optical_path, wavelength, tmp, isPositive=False)), 4)
    

    ### DENSITY FROM WAVELENGTH EQUATION
    density_wl = rb_density_full_wavelength(d1_res, d2_res, slope, optical_path, wavelength, tmp)
    density_err_wl = rb_density_full_wavelength(d1_res, d2_res, cov_err, optical_path, wavelength, tmp)
    diff = abs(density_raw-density_wl) 

    ### KILLIAN DENSITY
    killian_val = formatter(killian_density(tmp),4)

    #create my data frame
    output = pd.DataFrame({'Date': [collected_date],
                        'Cell Name': [cell],
                        'Temperature':[tmp],
                        'Density (with Paramagentic term)': [density_full],
                        'Density (from wavelength verison)':[formatter(density_wl, 5)],
                        'Density Error (Frequency calc)': [density_error_full],
                        'Density Error (Wavelength calc)':[formatter(density_err_wl, 5)], 
                        'Diff':[formatter(diff, 5)],
                        'Killian Value':[killian_val],
                        'Probe Beam':[formatter(wavelength, 5)] })
    return output