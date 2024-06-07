import json
import plotSettings as ps
import datetime
import numpy as np
import random
from os import path
from datetime import date
import csv
import pandas as pd

def getJsonData(path_to_file):
    """
    Opens a JSON file at the specified location.

    Parameters
    ----------
    path_to_file : string
        location at which the file is to be opened.

    Returns
    -------
    my_data_sets : python object
        Dictionary object constructed from the contents of the specified json file
    """

    with open(path_to_file, 'r') as json_File:
        load_file = json.load(json_File)
    my_data_sets = load_file['data']
    return my_data_sets

def count_data_sets(jsonData):
    """
    Given JSON data, returns the number of data sets within the file.

    Parameters
    ----------
    jsonData : python object
        object containing one or more datasets to be counted.

    Returns
    -------
    data_count : int
        The number of datasets contained within the file
    """

    data_count = 0
    for x in jsonData:
        data_count = data_count+1
    return data_count

def count_keys(dict_obj):
    """
    Given a dictionary object, returns the number of keys in the object

    Parameters
    ----------
    dict_obj : dictionary
        object containing one or more keys  to be counted.

    Returns
    -------
    key_count : int
        The number of keys contained within the dictionary.
    """
     
    key_count = 0
    for x in dict_obj:
        key_count = key_count +1
    return key_count

def find_specific_trial(jsonData, date, trialnum):
    """
    Given JSON data, a date, and a trial number, searches the JSON data for the specified 
    trial and returns the trial if found.

    Parameters
    ----------
    jsonData : python object
        object containing experimental data as dictionary objects.
    date : string
        date associated with the desired dataset.
    trialnum : int
        trial number associated with desired dataset.  

    Returns
    -------
    target_data : dictionary
        Desired dataset as a dictionary object. 
    """

    data_index = 0
    target_data = []
    for x in jsonData:
        #gets the object at the data_index position
        data_set = jsonData[data_index]
        #get the date of the current data's collection
        cdate = data_set.get('dateCollected')
        #get the trial number for the current data set
        tnum = data_set.get('trial')
        #compare date and trial number to those specified by the function
        if(cdate == date and tnum == trialnum): 
            #if they match end loop and return the x and y values 
            x_vals = data_set.get('magneticField')
            y_vals = data_set.get('rotation')
            x_err = data_set.get('magFieldError')
            y_err = data_set.get('rotationError')
            wavelength = data_set.get('laserWavelength')
            opt_len = data_set.get('opticalLength')
            target_data = ps.plotable(x_vals,y_vals,wavelength,opt_len,x_err,y_err)
            break
        #add one to index
        data_index = data_index+1
    return target_data

def get_data_from_file(path_to_file, date, trialnum):
    """
    Given a filepath, a date, and a trial number, searches the file for the 
    specified trial and returns the trial if found.

    Parameters
    ----------
    path_to_file : string
        Path to the JSON file containing the desired dataset.
    date : string
        date associated with the desired dataset.
    trialnum : int
        trial number associated with desired dataset.  

    Returns
    -------
    target_data : dictionary
        Desired dataset as a dictionary object. 
    """
    the_data = getJsonData(path_to_file)
    target_data = find_specific_trial(the_data, date, trialnum)
    return target_data

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

def prepRawDataForFile(raw_data):
    """
    Takes an array of raw data points (as an array of DataPoint objects and returns a 
    JSON object to be saved to a file containing all raw data from that round of collection
    
    Parameters
    ----------
    raw_data : numpy array 
        A numpy array containing current, voltage, and error values. 

    Returns
    -------
    raw : dictionary
        The raw data formatted to be written to a JSON file.  
    """

    #this time is approximately the time at which data collection completed for that set 
    current_time = str(datetime.datetime.now())
    #create an array of the current values
    current_array = []
    #create an array of the voltage readings
    voltage_array = []
    #create an array of the voltage reading errors
    voltage_err_array = []
    for i in raw_data:
        current_array.append(float(i.x_val))
        voltage_array.append(float(i.y_val))
        voltage_err_array.append(float(i.y_val/100))

    raw = {
        "date": current_time,
        "current": current_array,
        "voltage": voltage_array,
        "voltageError": voltage_err_array
    }
    return raw


#given a filepath and data to add to a JSON file
#opens the JSON file, reads out the data, and adds the new data to the end
#assumes data is a dictionary object
def saveDatatoJSON(file, data):
    """
    Given a filepath and data to add to a JSON file, opens the JSON file, reads out the data, 
    and adds the new data to the end. This assumes data is a dictionary object.
    
    Parameters
    ----------
    file_path : string
        file location as a string
    data : dictionary 
        data to save to the specified file
    """

    filename = str(file)
    #if the file doesn't exist, create it
    if path.isfile(filename) is False:
        #create empty dictionary object
        initial_data = {
            "data":[]
            }
        with open(filename, "w") as outfile:
            outfile.write(json.dumps(initial_data))

    #open the file and get the contents
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["data"].append(data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

#given an array of datapoints converted to the target measurements
#returns a dictionary object matching the format used by the rotationdata.json file
def prepConvertedDataforFile(converted_data, trial_num, laser_wl, opt_len, temp, power, conv_factor, laserT):
    """
    Given an array of datapoints converted to the target measurements, returns a dictionary object matching 
    the format used by the rotationdata.json file.
    
    Parameters
    ----------
    converted_data : dictionary
        data to be saved to file. Data should have been converted from raw state to magnetic field and rotation values  
    trial_num : int
        trial number associated with dataset 
    laser_wl : float
        wavelength of probe laser (in cm).
    opt_len : float
        optical length of cell (in cm). 
    temp : int
        Oven temperature at which the data was collected. 
    power : float
        laser power, as displayed on the laser control box. 
    conv_factor :  float
        conversion factor used to transform data from voltage values to rotation values
    laserT : float
        laser temperature, as displayed on the laser control box.

    Returns
    -------
    converted : dictionary
        The specified data formatted to be written to a JSON file.   
    """

    current_date = str(datetime.date.today())
    #create an array of the current values
    b_field_array = []
    #create an array of the voltage readings
    rotation_array = []
    #create an array of the voltage reading errors
    rotation_err_array = []
    for i in converted_data:
        b_field_array.append(float(i.x_val))
        rotation_array.append(float(i.y_val))
        rotation_err_array.append(np.abs(float(i.y_err)))

    converted = {
        "dateCollected": current_date,
        "trial": trial_num,
        "laserWavelength": laser_wl,
        "opticalLength": opt_len,
        "ovenTemp": temp,
        "laserPower": power,
        "rotationConversionFactor": conv_factor,
        "laserTemp": laserT,
        "magneticField": b_field_array,
        "rotation": rotation_array,
        "magFieldError": [],
        "rotationError": rotation_err_array
    }
    return converted
    
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

def randomNumber(orderOfMagnitude):
    """
    Generates a random number of the specified order of magnitude. 

    Parameters
    ----------
    orderOfMagnitude : int
        power of 10 specifying the order of magnitude for the randomly generated value

    Returns
    -------
    num : float
        a random number.   
    """
    num = orderOfMagnitude*random.random()
    return num

def percent_error(measurement, error_val):
    """
    Calculates the percent error from a specified measurement and error value.  Uses formula 100*error_val/measurement

    Parameters
    ----------
    measurement : float
        measurement with which to calculate percent error
    error_val : float
        error in measurement value.

    Returns
    -------
    percent_e : float
        the percent error value.
    """
     
    ratio = error_val/measurement
    percent_e = np.abs(ratio*100)
    return percent_e

def estimateStandardDev(range):
    """
    Uses the "Range Rule" to approximate standard deviation from the range of a data set. 
    The Range Rule is an approximation of standard deviation where std_dev = range/4. N
    Note that range rule assumes that the data is varying randomly and not systematically
    
    Parameters
    ----------
    range : float
        the range of the data for which the standard deviation is to be estimated. 

    Returns
    -------
    approx_sdev : float
        the standard deviation from the mean, as approximated by the range rule.
    """
    approx_sdev = range/4
    return approx_sdev


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

### TO BE DELETED??
#chekcs if a given object is a float or not
#def is_number(s):
#    try:
#        float(s)
#        return True
#    except ValueError:
#        return False

#for prompts requiring numerical input
#def get_response(prompt, breakresponses):
#    isItNumber = False
#    while (isItNumber == False):
#        resp = input(prompt)
#        isItNumber = is_number(resp)
#    return resp
#for prompts resulting in string responses!
#def get_choice(choices, input_prompt):
#  choice = ""
#  while choice not in choices:
#      choice = input(input_prompt).lower()
#  return choice