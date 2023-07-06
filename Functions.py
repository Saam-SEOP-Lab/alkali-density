import numpy as np

#this is where all the functions I might want to use with curve fit are defined

#line: y=ax+b
def line(x,a,b):
    y = a*x + b
    return y

#quadratic: y = a*x^2+b*x+c
def quadratic(x, a, b, c):
    y = a*x**2+b*x+c
    return y

#cubic: y=a*x^3+b*x^2+c*x+d
def cubic(x, a, b, c, d):
    y = a*x**3+b*x**2+c*x+d
    return y

#exponential: a*e^(b*x)+c
def exponential(x, a, b, c):
    y = a*np.exp(b*x)+c 
    return y

#natural log: a * np.log(b * x) + c 
def nlog(x, a, b, c):
    y = a*np.log(b*x) + c
    return y

#Gaussian: a*e^((x-b)^2/c) + d
def Gaussian(x, a, b, c, d):
    y = a * np.exp((x-b) ** 2 / c) + d
    return y

