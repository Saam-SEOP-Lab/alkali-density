from math import log10
from .conversions import convertTtoKelvin
from  .constants import BOHR_MAGNETON, ELECTRON_CHARGE, ELECTRON_MASS, LIGHT_SPEED, PLANKS_CONSTANT, BOLTZMANN_CONSTANT

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
    prefactor = (optical_length*ELECTRON_CHARGE**2*BOHR_MAGNETON)/(6*ELECTRON_MASS*LIGHT_SPEED*PLANKS_CONSTANT)
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
    fo_prefactor = probe_beam**2/(3*LIGHT_SPEED**2)
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
    so_prefactor = (PLANKS_CONSTANT*probe_beam)/(LIGHT_SPEED*BOLTZMANN_CONSTANT*T_in_Kelvin) #for future me: when you come back here in several months and panic that there is an extra factor of c that doesn't make sense, it is necessary due to distribution and algebra. It arises from combining the version of the equation in Vleigen and the version of the equation in Chann
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
    numerator = 0.106*Td*optical_length*BOHR_MAGNETON*oscillator_strength*line_width**2*kappa*resonance**6*ELECTRON_CHARGE**2
    denominator = ELECTRON_MASS*LIGHT_SPEED**4*PLANKS_CONSTANT*(probe_beam-resonance)**3
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