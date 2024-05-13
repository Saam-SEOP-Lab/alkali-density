import numpy as np

#this is where all the functions I might want to use with curve fit are defined

#line: y=ax+b
def line(x,a,b):
    """
    line: y = a*x + b

    Parameters
    ----------
    x : float
        independent variable
    a : float
        slope
    b : float
        y intercept

    Returns
    -------
    y : float
        the value of y given values for x, a, and b. 
    """
    y = a*x + b
    return y

def line_zero_intercept(x, a):
    """
    line, with intercept at 0: y = a*x

    Parameters
    ----------
    x : float
        independent variable
    a : float
        slope

    Returns
    -------
    y : float
        the value of y given values for x and a. 
    """
    y = a*x
    return y

#quadratic: y = a*x^2+b*x+c
def quadratic(x, a, b, c):
    """
    quadratic : y = a*x^2+b*x+c

    Parameters
    ----------
    x : float
        independent variable
    a : float
        quadratic term
    b : float
        linear term
    c : float
        constant term

    Returns
    -------
    y : float
        the value of y given values for x, a, b, and c. 
    """
    y = a*x**2+b*x+c
    return y

def cubic(x, a, b, c, d):
    """
    quadratic : y=a*x^3+b*x^2+c*x+d

    Parameters
    ----------
    x : float
        independent variable
    a : float
        cubic term
    b : float
        quadratic term
    c : float
        linear term
    d : float
        constant term

    Returns
    -------
    y : float
        the value of y given values for x, a, b, c, and d. 
    """
    y = a*x**3+b*x**2+c*x+d
    return y

#exponential: a*e^(b*x)+c
def exponential(x, a, b, c):
    """
    exponential : y = a*e^(b*x)+c

    Parameters
    ----------
    x : float
        independent variable
    a : float
        coefficient of e
    b : float
        coefficient of x
    c : float
        constant term

    Returns
    -------
    y : float
        the value of y given values for x, a, b, and c. 
    """
    y = a*np.exp(b*x)+c 
    return y

#natural log: a * np.log(b * x) + c 
def nlog(x, a, b, c):
    """
    natural log : y = a * np.log(b * x) + c 

    Parameters
    ----------
    x : float
        independent variable
    a : float
        coefficient of natural log
    b : float
        coefficient of x
    c : float
        constant term

    Returns
    -------
    y : float
        the value of y given values for x, a, b, and c. 
    """
    y = a*np.log(b*x) + c
    return y

#Gaussian: a*e^((x-b)^2/c) + d
def Gaussian(x, a, b, c, d):
    """
    Gaussian : y = a*e^((x-b)^2/c) + d

    Parameters
    ----------
    x : float
        independent variable
    a : float
        coefficient of e
    b : float
        part of (x)^2 term
    c : float
        (x-b)^2 term denominator
    d : constant term

    Returns
    -------
    y : float
        the value of y given values for x, a, b, c and d. 
    """
    y = a * np.exp((x-b) ** 2 / c) + d
    return y

