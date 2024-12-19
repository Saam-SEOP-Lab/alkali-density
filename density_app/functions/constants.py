import numpy as np

### PHYSICAL CONSTANTS

"""
    Value: Bohr Magneton
    Units: erg/Gauss
"""
BOHR_MAGNETON = 9.274E-21

"""
    Value: Charge of an Electron
    Units: cm^(3/2)*g^(1/2)/s
"""
ELECTRON_CHARGE = 4.8032E-10

"""
    Value: Mass of an Electron
    Units: g
"""
ELECTRON_MASS = 9.1094E-28

"""
    Value: Plank's Constant
    Units: erg*s
"""
PLANKS_CONSTANT = 6.626176E-27

"""
    Value: Speed of Light
    Units: cm/s
"""
LIGHT_SPEED = 29979245800 

"""
    Value: Boltzmann Constant
    Units: erg/K
"""
BOLTZMANN_CONSTANT = 1.380649E-16




# EXPERIMENTAL CONSTANTS 

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
d1_resonance_f = LIGHT_SPEED/d1_resonance_lambda #rb 85, cell 309A

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
d2_resonance_f = LIGHT_SPEED/d2_resonance_lambda #pressure low pressure cell line 314

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