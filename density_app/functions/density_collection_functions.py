import numpy as np # http://www.numpy.org/
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import time

#imports for my modules
import functions.utilities as util
#from functions.utilities import meanAbsError

#meanAbsError


def collectDataPoint(num_avg, time_interval, scope):
    i = 0
    data_point_calc = np.zeros(num_avg)
    data_point = np.zeros(3)
    for i in range (0, num_avg):
        data_point_calc[i] = scope.query('MEASU:IMM:VAL?')
        time.sleep(time_interval)
        i = i+1
    data_point[0]=np.average(data_point_calc) #average of all collected points for that current
    data_point[1]=util.meanAbsError(data_point_calc) #error using mean absolute error
    data_point[2]=np.std(data_point_calc) #standard deviation from the mean
    return data_point


def collectCurrent(resource):
        prompt ='Enter current value in Amps'
        current = input(prompt)
        return current

def list_instruments():
    rm = visa.ResourceManager()
    inst = rm.list_resources()
    return inst

def connectToScope(scope_address):
    rm = visa.ResourceManager()
    rm.list_resources()
    oscilloscope = rm.open_resource(scope_address)
    return oscilloscope

def setUpScopeForDataCol(resource):
    resource.encoding = 'latin_1'
    resource.source_channel = 'CH1'

    resource.write('DATA:SOU CH1') 
    resource.write('DATA:WIDTH 1') 
    resource.write('DATA:ENC RPB')

    #set trigger to auto
    resource.write('TRIGGER:MAIN:MODE AUTO')

    #set the aquisition mode to sample
    resource.write('AQCUIRE:MODE SAMPLE')
    #set acquisition mode to runstop
    resource.write('ACQUIRE:STATE STOP')
    resource.write('ACQUIRE:STOPAFTER: RUNSTOP')
    resource.write('ACQUIRE:STATE RUN')

    #set the number of points to average
    #resource.write('ACQUIRE:NUMAVG ' + str(N))

def list_resources(rm):
    res = []
    for r in rm.list_resources():
        res.append(r)

    return res

     
def calculateCalibrationFactor(lock_in_sensitivity, v_i, v_f, angle):
    #calculate scaling factor from lockin sensitivity
    scaled_diff = abs(v_f-v_i)*(lock_in_sensitivity/10)
    calibration_factor = (angle / scaled_diff)*(np.pi/180) #convert to radians/volt out of photodiode
    return calibration_factor

def calculateCalibrationError(lock_in_sensitivity, v_i_err, v_f_err, angle):
    total_V_err = (lock_in_sensitivity/10) * (abs(v_i_err) + abs(v_f_err))
    #return the error in same units as calibration factor
    cal_factor_error = (angle/total_V_err)*(np.pi/180) #convert error to radians per volt
    (angle*np.pi)/(180*total_V_err)
    return cal_factor_error

def calculate_conversion_factor(lock_in_sensitivity, calibration_factor):
    conversion_factor = (lock_in_sensitivity/10)*calibration_factor
    return conversion_factor


