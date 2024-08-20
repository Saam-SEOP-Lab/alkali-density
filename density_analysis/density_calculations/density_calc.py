import numpy as np
from typing import Type
from math import log10

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
d1_resonance_f = 3.77107568E+14 #rb 85, cell 309A


#D2 transition resonance wavelength
#units: cm
d2_resonance_lambda = 7.80402E-5

#D2 transition resonance frequency
#units: Hz
#d2_resonance_f = 3.8420406E+14
d2_resonance_f = 3.842306E+14 #pressure shifted for cell 309A

#constants in the B field equation for helmholz coils
#B = [(4/5)^(3/2)*4*pi*10^-3]*[IN/R]
#I is current, N is number of turns of wire in coil and R is radius
#this is for the coils used in the front room set up
b_const = ((4 / 5)**(3/2)) * 4E-3 * np.pi

#verdet constand of Pyrex Glass at 773nm, in radians/cm*Gauss
verdet_glass = (2.3e-6)*.3 
######################## FUNCTIONS #################################

#given the laser frequency, returns the difference from D1 resonance
#units: cgs
def get_Delta_D1(laser_freq):
    delta_D1 = d1_resonance_f - laser_freq
    return delta_D1

#given the laser frequency, returns the difference from D2 resonance
#units: cgs
def get_Delta_D2(laser_freq):
    delta_D2 = d2_resonance_f - laser_freq
    return delta_D2

#given laser wavelength, returns laser frequency
#units: cgs
def get_laser_f(laser_lambda):
    laser_f = light_speed/laser_lambda
    return laser_f

#given laser wavelength, return the delta term in the density calculation
def delta_term(laser_wavelen):
    laser_fr = get_laser_f(laser_wavelen)
    D1 = get_Delta_D1(laser_fr)
    D1_sq = D1**2
    D2 = get_Delta_D2(laser_fr)
    D2_sq = D2**2
    delta_numerator = D1_sq * D2_sq
    delta_denominator = (4 * D2_sq) + (7 * D1_sq) - (2 * D1 * D2)
    delta_term = delta_numerator/delta_denominator
    return delta_term

#given optical path length return optical path term in density caculation
def optical_length_term(o_len):
    ol_numerator = 18 * m_electron * h * light_speed
    ol_denominator = o_len * q_electron**2 * mu_b
    ol = ol_numerator/ol_denominator
    return ol

#given the slope of the rotation vs magnetic field graph, the optical path length 
#and the laser wavelength, return the density of rubidium in the cell
def rb_density(slope, o_len, laser_wave):
    deltas_term = delta_term(laser_wave)
    opt_len_term = optical_length_term(o_len)
    density = slope * opt_len_term * deltas_term
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
def glass_verdet_adj(verdet, glass_depth, rot_val, mag_field_val):
    verdet_adjment = (verdet*glass_depth)*mag_field_val
    adjusted_rot = rot_val-verdet_adjment
    return adjusted_rot

# takes a temp in Celcuis and returns the Killian estimated density value of Rb
def killian_density(temp):
    T = float(temp) + 273.15
    a=26.41
    b=4132/T
    c = log10(T)
    rb_den = 10 **(a-b-c)
    return rb_den
