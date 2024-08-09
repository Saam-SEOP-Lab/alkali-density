import datetime
import numpy as np
from datetime import date
import csv
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

def exportToCSV(fp, fields, formatted_data):
    """
    Exports the provided data to a csv file. 
    
    Parameters
    ----------
    fp : string
        location to save the data to, as a string.
    fields : array of strings
        the headers for the csv as an array. 
    formatted_data : 2D array 
        the data to save to the csv file as two dimensional array. 
    """

    filename = str(fp)
    #first check that no files with the same name exist
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(fields)
        # writing the data rows
        csvwriter.writerows(formatted_data)   


def stringArraytoFloatArray(str_arry):
    l = len(str_arry)
    num_arry = np.zeros(l)
    for i in range(0,l):
        num_arry[i] = float(str_arry[i])
    return num_arry

def stringToPandasSeries(strg, delimiter):
    #assumes a string where data can be broken up by a delimiter
    #check if there is a newline at the end of the string and remove if present
    strg = strg.replace('\n', '')
    arry = strg.split(delimiter)
    series = pd.Series(arry)
    return series

def dtStringForFilename():
    fn = str(datetime.datetime.today())
    fn = fn.replace(':', '_')
    fn = fn.replace(' ', '-')
    return fn

#takes a time stamp (float) and converts it into an array in the format [date, time]
def timestampToArray(ts):
    dt_obj = datetime.datetime.fromtimestamp(ts)
    dt_arry = str(dt_obj).split(' ')
    return dt_arry

#takes an array of the form [[A1, B1], [A2, B2], ... , [AN, BN]] 
#and returns two arrays of the form [A1, A2, ... , AN] and [B1, B2, ... , BN]
def twoDArryToTwoOneDArry(arry):
    arry_0 = []
    arry_1 = []

    for x in arry:
        arry_0.append(x[0])
        arry_1.append(x[1])
    return (arry_0, arry_1)

#takes an array of timestamps and converts it to two arrays, one containing all the dates, the other containing all the times
def formatTimestampsForCSV(times):
    arry_0 = []
    arry_1 = []

    for x in times:
        temp = timestampToArray(x)
        arry_0.append(temp[0])
        arry_1.append(temp[1])
    
    return (arry_0, arry_1)

def meanAbsError(data_set):
    sum = 0
    num_pts = len(data_set)
    avg = np.average(data_set)
    for i in range(num_pts): 
        sum += abs(data_set[i] - avg) 
    error = sum/num_pts
    return error

def createFilePath(folder, collection_type):
    filename = collection_type + dtStringForFilename()
    fp = folder + filename
    return fp

def createDataCSV(fp, empty_dataframe):
    file = open(fp, 'a')
    empty_dataframe.to_csv(fp, mode='a', index=False)
    return file

def createDataCSV_Indexed(fp, empty_dataframe):
    file = open(fp, 'a')
    empty_dataframe.to_csv(fp, mode='a', index=True)
    return file

def createParamsCSV(fp, params):
    file = open(fp, 'w')
    params.to_csv(fp, mode='w', index=False)
    file.close()

def validate_is_float(text):
	try:
		float(text)
		isFloat=True
	except ValueError:
		isFloat=False
	return isFloat

def validate_text_exists(text):
    l = len(text)
    entryExists = False
    if (l > 0):
        entryExists=True
    return entryExists

def entry_exists_is_number(text):
		exists = validate_text_exists(text)
		isNum = validate_is_float(text)
		acceptableNumerical = False
		if (exists and isNum):
			acceptableNumerical = True
		return acceptableNumerical
