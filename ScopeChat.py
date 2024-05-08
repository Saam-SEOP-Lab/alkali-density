import numpy as np # http://www.numpy.org/
import pyvisa as visa # http://github.com/hgrecco/pyvisa
from struct import unpack
import time
from DataPoint import DataPoint
import Utilities as util


class Oscope: 
    def __init__(self, visa_address,num_avg,source_channel, scope=None):
        self.visa_address = visa_address
        self.rm = visa.ResourceManager()
        self.encoding = 'latin_1'
        self.read_termination = '\n'
        self.write_termination = '\n'
        self.num_avg = num_avg
        self.source_channel = source_channel
        self.scope = scope

#moving the scope start up and initialization to it's own function  
    def startScope(self):
        scope = self.scope
        scope = self.rm.open_resource(self.visa_address)
        scope.timeout = 5000 # ms
        scope.encoding = 'latin_1'
        scope.read_termination = '\n'
        scope.write_termination = '\n'#None
        scope.write('*cls') # clear ESR
        self.scope = scope

    #sets the following parameters: 
    # channel to read as channel 1,  
    # datawidth to 1 
    # encoding to binary
    # number to of points to average to specified value
    ### 
    def collectionSetUp(self):
        # Setting source as Channel 1
        scope = self.scope
        scope.write('DATA:SOU CH1') 
        scope.write('DATA:WIDTH 1') 
        scope.write('DATA:ENC RPB')
        #set the number of points to average
        avg_cmd = 'ACQUIRE:NUMAVG '+str(self.num_avg)#PROBABLY DON'T NEED THIS?
        avg = float(self.scope.query('ACQUIRE:NUMAVG?')) # get the number of averages set?
        if (avg != self.num_avg):
            scope.write(avg_cmd)
        #set the acquisition mode to runstop if set to something else
        if(scope.query('ACQUIRE:STOPAFTER?') != 'RUNSTOP'):
            scope.write('ACQUIRE:STATE OFF')
            scope.write('ACQUIRE:STOPAFTER: RUNSTOP')
            scope.write('ACQUIRE:STATE ON')
        #set the acquisition mode to sample if set to something else
        if(scope.query('ACQUIRE:MODE?') != 'SAMPLE'):
            scope.write('AQCUIRE:MODE SAMPLE')
        #set the trigger mode to normal if set to something else
        if(scope.query('TRIGGER:MAIN:MODE?')!= 'AUTO'):
            scope.write('TRIGGER:MAIN:MODE AUTO')

        self.scope = scope

    #prompts for current value in amps
    #saves to an array
    def collectCurrent(self):
        prompt ='Enter current value in Amps'
        current = input(prompt)
        return current

    #given an immediate measurement type to collect, 
    #constructs the command for that measurement
    def setMeasurementTypeCommand(self, type):
        #construct the command
        m_type_cmd = 'MEASUREMENT:IMMED'+':TYPE '+str(type)
        return m_type_cmd
    
    def getMeasurementValCommand(self):
        #construct the command
        m_val_cmd = 'MEASUrement:IMMed:VALue?'
        return m_val_cmd
    
    #collects a  data point
    #this datapoint is a signal average over self.avg_num number of values
    #the uncertainty is computes and the units are read
    #returns an array of the form [mean, uncertainty, units]
    def collectMean(self):

        set_size = 20

        #create an array of 0's so I can collect a several values at one current value
        #then average
        data_point = np.zeros(set_size)

        #set measurement type to mean
        set_type_mean = self.setMeasurementTypeCommand('MEAN')
        self.scope.write(set_type_mean)
        #set source to collect from
        self.scope.write('MEASUREMENT:IMMED:SOURCE CH1')
        #collect mean 5 times
        collect_mean = self.getMeasurementValCommand()

        total = 0
        for i in range(0,set_size):
            data_point[i] = float(self.scope.query(collect_mean))
            total = total + data_point[i]

        mean_val = total/set_size
        print(data_point)
        max_val = data_point.max()
        min_val = data_point.min()
        rng = np.abs(max_val-min_val)

        uncert = util.estimateStandardDev(rng)
        mean = [mean_val, uncert]
        print(mean)
        return mean
    

    def collectUntilDone(self, time_constant):
        data = np.array([])
        while True: 
            x = self.collectCurrent()
            if (str(x) == "quit"):
                break
            #waits 5x the time constant on the lock-in before collecting a mean value 
            time.sleep(5*time_constant)
            y = self.collectMean()
            collection_point = DataPoint(x, y[0], y[1])
            data = np.append(data, collection_point)
        return data

    #prompts the user to take a calibration measurement
    #if the user chooses no either time, 0 will be returned as the calibration value
    #and the calibration value will need to be passed to the conversion function manually later on
    #OLD VERSION
    def collectCalibrationMeasurement_DEPRICATED(self):
        prompt_takeMeas = 'Would you like to take a calibration measurement? y/n'
        reply_takeMeas = input(prompt_takeMeas)
        initial = np.array([])
        final = np.array([])
        calibration_value = np.array([])
        if(reply_takeMeas == 'y'):
            #collect the unrotated value
            prompt_collectPreRotation = 'Collect unrotated value? y/n'
            reply_collectPreRotation = input(prompt_collectPreRotation)
            if(reply_collectPreRotation == 'y'):
                initial = self.collectMean()
                prompt_collectPostRotation = 'Rotate halfwave plate. enter y to collect mean'
                reply_collectPostRotation = input(prompt_collectPostRotation)
                if(reply_collectPostRotation == 'y'):
                    final = self.collectMean()
                    cal_value = final[0] - initial[0]
                    calibration_value = np.append(calibration_value, cal_value)
                    cal_error = final[1] + initial[1]
                    calibration_value = np.append(calibration_value, cal_error)
                    calibration_value = np.append(calibration_value, initial[0])
                    calibration_value = np.append(calibration_value, final[0])
        return calibration_value
    
    #UPDATED VERSION
    #prompts the user to take a calibration measurement
    #if the user chooses no either time, 0 will be returned as the calibration value
    #and the calibration value will need to be passed to the conversion function manually later on
    def collectCalibrationMeasurement(self):
        initial = np.array([])
        final = np.array([])
        calibration_value = np.array([])
        #collect the unrotated value
        prompt_collectPreRotation = 'Begining calibration process. Enter y to collect first measurement.'
        reply_collectPreRotation = input(prompt_collectPreRotation)
        if(reply_collectPreRotation == 'y'):
            initial = self.collectMean()
            prompt_collectPostRotation = 'Rotate the halfwave plate one degree (4 turns on the small knob). When completed enter y to collect rotated value'
            reply_collectPostRotation = input(prompt_collectPostRotation)
            if(reply_collectPostRotation == 'y'):
                final = self.collectMean()
                calibration_value = np.append(calibration_value, initial)
                calibration_value = np.append(calibration_value, final)
        #add else or if else to handle mistypes

        return calibration_value
    
    #close all the things
    def scopeClose(self):
        self.scope.close()
        self.rm.close()


    

