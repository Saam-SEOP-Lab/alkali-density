import numpy as np # http://www.numpy.org/
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import time

#imports for my modules
from functions.fitting_and_error import meanAbsError

def collectDataPoint(num_avg, time_interval, scope):
    """
    Records a data point for alkali metal density measurement. The user specifies how many data points they would like to average when collecting each data point as well as how long to wait between readings within a set. That number of readings will be collected from the specified oscilloscope. They will then be averaged and the mean absolute error and standard deviation of the set will be reported in volts. 
    
    Parameters
    ----------
    num_avg : int
        The number of voltage readings to average when calculating an average voltage reading. 
    time_interval : float
        The amount of time in seconds to wait between readings. 
    scope : Resource
        A pyvisa Resource representing the oscilloscope being used to record voltages. 

    Returns
    -------
    data_point : array 
        A float array representing a data point, of the form [Average Voltage, Mean Absolute Error, Standard Deviation]
    """
    i = 0
    data_point_calc = np.zeros(num_avg)
    data_point = np.zeros(3)
    for i in range (0, num_avg):
        data_point_calc[i] = scope.query('MEASU:IMM:VAL?')
        time.sleep(time_interval)
        i = i+1
    data_point[0]=np.average(data_point_calc) #average of all collected points for that current
    data_point[1]=meanAbsError(data_point_calc) #error using mean absolute error
    data_point[2]=np.std(data_point_calc) #standard deviation from the mean
    return data_point


def collectCurrent(resource):
        prompt ='Enter current value in Amps'
        current = input(prompt)
        return current

def list_instruments():
    """
    Obtains a list of the resources currently connected to the computer. 
    
    Parameters
    ----------

    Returns
    -------
    inst : array 
        An array listing the available pyvisa resources. 
    """
    rm = visa.ResourceManager()
    inst = rm.list_resources()
    return inst

def connectToScope(scope_address):
    """
    Establishes a connection to the oscilloscope. 
    
    Parameters
    ----------
    scope_address : string
        The visa address of the target instrument. 

    Returns
    -------
    oscilloscope : Resource 
        A pyvisa resource representing the specified oscilloscope. 
    """
    rm = visa.ResourceManager()
    rm.list_resources()
    oscilloscope = rm.open_resource(scope_address)
    return oscilloscope

def setUpScopeForDataCol(resource):
    """
    Sends a series of commands to the specified oscilloscope resource to ensure that it is in the correct state for data collection. 

    Parameters
    ----------
    resource : Resource
        A resource object representing the oscilloscope. 

    Returns
    -------
    """
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
    """
    Lists all resources seen by the specified resource manager.  

    Parameters
    ----------
    rm : Resource Manager
        A pyvisa resource manager object.

    Returns
    -------
    res : array
        An array of all Resouce objects seen by the resource manager. 
    """
    res = []
    for r in rm.list_resources():
        res.append(r)
    return res
     
def calculateCalibrationFactor(lock_in_sensitivity, v_i, v_f, angle):
    """
    Calculates the calibration factor accounting for the scaling factor from the lock-in amplifier sensitivity. 

    Parameters
    ----------
    lock_in_sensitivity : float
        A float representing the sensitivity value of the lock-in amplifier. 
    v_i : float
        The initial voltage value ready by the photodiode, before the calibration rotation of the half-wave plate. 
        units: Volts
    v_f : float
        The final voltage value ready by the photodiode, after the calibration rotation of the half-wave plate. 
        units: Volts
    angle : float
        The known angle value used for collecting the calibration value. 
        units: radians

    Returns
    -------
    calibration_factor : float
        The calibration factor collected for a particular experiment, accounting for the lock-in sensitivity settings.     
    """
    scaled_diff = abs(v_f-v_i)*(lock_in_sensitivity/10)
    calibration_factor = (angle / scaled_diff)*(np.pi/180) #convert to radians/volt out of photodiode
    return calibration_factor

def calculateCalibrationError(lock_in_sensitivity, v_i_err, v_f_err, angle):
    """
    Calculates the calibration factor error.

    Parameters
    ----------
    lock_in_sensitivity : float
        A float representing the sensitivity value of the lock-in amplifier used for calibration. 
    v_i_err : float
        The the error on the initial voltage calibration reading. 
        units: Volts
    v_f_err : float
        The error on the final voltage calibration reading.  
        units: Volts
    angle : float
        The known angle value used for collecting the calibration value. 
        units: radians

    Returns
    -------
    cal_factor_error : float
       The error on the calibration factor.     
    """
    total_V_err = (lock_in_sensitivity/10) * (abs(v_i_err) + abs(v_f_err))
    #return the error in same units as calibration factor
    cal_factor_error = (angle/total_V_err)*(np.pi/180) #convert error to radians per volt
    (angle*np.pi)/(180*total_V_err)
    return cal_factor_error

def calculate_conversion_factor(lock_in_sensitivity, calibration_factor):
    """
    The calibration rotation is much larger than the rotations seen when making density measurements. As a result the lock-in typically needs to be set to a different sensitivity when collecting data. This function converts the calibration factor into the correct scale for use on rotation data. 

    Parameters
    ----------
    lock_in_sensitivity : float
        A float representing the sensitivity value of the lock-in amplifier used for data collection. 
    calibration_factor : the calibration factor as calculated in the calibration measurement step. 
        units: radians/Volt

    Returns
    -------
    conversion_factor : float
       The calibration factor collected for a particular experiment, accounting for the lock-in sensitivity settings both during calibration and collection.     
    """
    conversion_factor = (lock_in_sensitivity/10)*calibration_factor
    return conversion_factor


