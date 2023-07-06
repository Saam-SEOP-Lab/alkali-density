import json
import plotSettings as ps
import datetime
import numpy as np

from os import path
from datetime import date


#open a json file
def getJsonData(path_to_file):
    with open(path_to_file, 'r') as json_File:
        load_file = json.load(json_File)
    my_data_sets = load_file['data']
    return my_data_sets

#counts the number of data sets within a given json file
def count_data_sets(jsonData):
    data_count = 0
    for x in jsonData:
        data_count = data_count+1
    return data_count

#counts the number of keys a data set has
def count_keys(dict_obj):
    key_count = 0
    for x in dict_obj:
        key_count = key_count +1
    return key_count

#given a particular date and trial number, returns the data associated with those two key values
def find_specific_trial(jsonData, date, trialnum):
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
    the_data = getJsonData(path_to_file)
    target_data = find_specific_trial(the_data, date, trialnum)
    return target_data

#rounds to the specified number of decimal places and formats the number into scientific notation
def formatter(n, p):
    precision = p
    num = f"{n:.{precision}e}"
    return num

#takes an array of raw data points (as an array of DataPoint objects)
#returns a JSON object to be saved to a file containing all raw data from that round of collection
def prepRawDataForFile(raw_data):
    #this time is approximately the time at which data collection completed for that set 
    current_time = str(datetime.datetime.now())
    #create an array of the current values
    #create an array of the voltage readings
    #create an array of the voltage reading errors    
    current_array = []
    voltage_array = []
    voltage_err_array = []
    for i in raw_data:
        current_array.append(float(i.x_val))
        voltage_array.append(float(i.y_val))
        voltage_err_array.append(float(i.x_val))

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
    current_date = str(datetime.date.today())
    #create an array of the current values
    #create an array of the voltage readings
    #create an array of the voltage reading errors    
    b_field_array = []
    rotation_array = []
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

#given a laser temp reading, returns the approximate wavelength
#note that this version uses a curve fit I found for the chart of laser wavelengths
#should be updated once I do the OSA readings to verify the laser wavelengths
def convertTemptoWavelength(laser_temp):
    m = -1
    b = 781.75
    wavelength = m*laser_temp + b
    wavelength = wavelength/(10**7)
    return wavelength


#for prompts resulting in string responses!
def get_choice(choices, input_prompt):
  choice = ""
  while choice not in choices:
      choice = input(input_prompt).lower()
  return choice

#chekcs if a given object is a float or not
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#for prompts requiring numerical input
def get_response(prompt):
    isItNumber = False
    while (isItNumber == False):
        resp = input(prompt)
        isItNumber = is_number(resp)

    return resp
    
#outputs the current date as a string in the form mmddyyyy
def getDateString():
    today = date.today()
    datestring = today.strftime("%m%d%Y")
    return datestring
