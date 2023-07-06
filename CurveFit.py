import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import plotSettings as ps

class CurveFit:
    def __init__(self, coefficients, covariences):
        self.coeff = coefficients
        self.cov = covariences
        

