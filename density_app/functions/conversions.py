import numpy as np
from .constants import LIGHT_SPEED, b_const

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
    freq = LIGHT_SPEED/wavelength
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