import datetime
import numpy as np
from datetime import date
import pandas as pd

def formatter(n, p):
    """
    Rounds to the specified number of decimal places and formats the number into scientific notation.

    Parameters
    ----------
    n : float
        Value to be formatted.
    p : int
        Number of decimal places to round the specified value to.

    Returns
    -------
    num : float
        Specified value rounded to specified precision.  
    """

    precision = p
    num = f"{n:.{precision}e}"
    return num

    
def getDateString():
    """
    Outputs the current date as a string in the form mmddyyyy.
    
    Parameters
    ----------

    Returns
    -------
    datestring : string
        The current date, formatted as MMDDYYYY.   
    """
    today = date.today()
    datestring = today.strftime("%m%d%Y")
    return datestring

def stringArraytoFloatArray(str_arry):
    """
    Converts an array of strings to an array of floats. 
    
    Parameters
    ----------
    str_arry : array
        An array of strings representing numbers. 

    Returns
    -------
    num_arry : array
        The same array, but with float elements instead of string elements.   
    """
    l = len(str_arry)
    num_arry = np.zeros(l)
    for i in range(0,l):
        num_arry[i] = float(str_arry[i])
    return num_arry

def stringToPandasSeries(strg, delimiter):
    #assumes a string where data can be broken up by a delimiter
    #check if there is a newline at the end of the string and remove if present
    """
    Breaks a string of data into its components on the specified delimiter. Checks if there is a newline at the end of the string and remove if present. Returns the resulting data as a pandas series. 
    
    Parameters
    ----------
    strg : string
        A string of data elements separated by some delimiter character. 
    delimiter : string
        The string or character separating the data elements within the string.  

    Returns
    -------
    series : Series
        The data from the string represented as a pandas Series.   
    """
    strg = strg.replace('\n', '')
    arry = strg.split(delimiter)
    series = pd.Series(arry)
    return series

def dtStringForFilename():
    """
    Formats a datetime string for the current day to be used in a file name, so that it follows consistent filenaming conventions. Datetimes are given by the system as: "YYYY-MM-DD HH:mm:SS.ssssss". This function formats them as: "YYYY-MM-DD-HH_mm_SS.ssssss". This is done to avoid issues with spaces in filenames and ensure a consistent formatting of filenames across experiments. 
    NOTE: Y=year, M=month, D=day, H=hour, m=minute, S=second, s=millisecond
    
    Parameters
    ----------

    Returns
    -------
    fn : string
        Returns a string in the format "YYYY-MM-DD-HH_mm_SS.ssssss".   
    """
    fn = str(datetime.datetime.today())
    fn = fn.replace(':', '_')
    fn = fn.replace(' ', '-')
    return fn

def timestampToArray(ts):
    """
    Takes a time stamp (float) and converts it into an array in the format [date, time]

    Parameters
    ----------
    ts : float
        A float representing a timestamp. 

    Returns
    -------
    dt_arry : array
        Returns a string array of the form [date, time]   
    """
    dt_obj = datetime.datetime.fromtimestamp(ts)
    dt_arry = str(dt_obj).split(' ')
    return dt_arry

#takes an array of the form [[A1, B1], [A2, B2], ... , [AN, BN]] 
#and returns two arrays of the form [A1, A2, ... , AN] and [B1, B2, ... , BN]
def twoDArryToTwoOneDArry(arry):
    """
    Takes an array of the form [[A1, B1], [A2, B2], ... , [AN, BN]] and returns two arrays of the form [A1, A2, ... , AN] and [B1, B2, ... , BN].

    Parameters
    ----------
    arry : array
        Any array of the form [[A1, B1], [A2, B2], ... , [AN, BN]].

    Returns
    -------
    arry_0 : array
        An array of the form  [A1, A2, ... , AN].
    arry_1 : array 
        An array of the form [B1, B2, ... , BN].
    """
    arry_0 = []
    arry_1 = []

    for x in arry:
        arry_0.append(x[0])
        arry_1.append(x[1])
    return (arry_0, arry_1)

def datapoints_nice(xs, ys, x_name, y_name):
    """
    Creates a dataframe for a set of data containing two components. 

    Parameters
    ----------
    xs : array
        Any array x values.
    ys : array
        Any array y values.
    x_name : string
        The name of the x data points.
    y_name : string
        The name of the y data points. 

    Returns
    -------
    arry_0 : array
    """
    df = pd.DataFrame({x_name: xs, 
                       y_name: ys })
    return df