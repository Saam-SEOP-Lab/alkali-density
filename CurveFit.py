import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import plotSettings as ps

class CurveFit:
    """
    A class used to store coefficients and covariance data from scipy optimize's curve fit function. 

    ...

    Attributes
    ----------
        coeff : array 
            An array containing values correspoinding to the coefficients found when fitting data to a particular curve.  
        cov : array
            Contains the covariance matrix values from the curve fit. 

    Methods
    -------
    __init__(self, coefficients, covariences)
        Creates a CurveFit object.
    """
    
    def __init__(self, coefficients, covariences):
        """
        Creates a CurveFit object.

        Parameters
        ----------
        self : CurveFit
            the CurveFit object to be created. 
        coeff : array
            An array containing values correspoinding to the coefficients found when fitting data to a particular curve.  
        cov : array
            Contains the covariance matrix values from the curve fit. 

        Returns
        -------
        CurveFit
            Returns a new CurveFit object.  
        """
        self.coeff = coefficients
        self.cov = covariences
        

