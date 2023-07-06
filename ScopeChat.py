
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


    #given measurement parameter number and measurement type
    #sets that measurement field to the specified type
    def setMeasurementType(self, meas_num, type):
        #construct the command
        meas_cmd = 'MEASUREMENT:MEAS'+str(meas_num)+':TYPE '+str(type)
        #send command to scope
        scope = self.scope
        scope.write(meas_cmd)
        self.scope = scope

    def setUpMeanCollection(self):
        #sets MEAS1 to Mean
        self.setMeasurementType(1, 'MEAN')
        #sets MEAS2 to Peak to Peak
        #this should return the difference between the max and min amplitudes
        #aka the range, which I can then use to calculate uncertainty in the mean
        self.setMeasurementType(2, 'PK2PK')


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
        avg_cmd = 'ACQUIRE:NUMAVG '+str(self.num_avg)
        avg = float(self.scope.query('ACQUIRE:NUMAVG?')) # get the number of averages set?
        if (avg != self.num_avg):
            scope.write(avg_cmd)
        #set the acquisition mode to runstop if set to something else
        if(scope.query('ACQUIRE:STOPAFTER?') != 'RUNSTOP'):
            scope.write('ACQUIRE:STATE OFF')
            scope.write('ACQUIRE:STOPAFTER: RUNSTOP')
            scope.write('ACQUIRE:STATE ON')
        #set the acquisition mode to average if set to something else
        if(scope.query('ACQUIRE:MODE?') != 'AVERAGE'):
            scope.write('AQCUIRE:MODE AVERAGE')
        #set the trigger mode to normal if set to something else
        if(scope.query('TRIGGER:MAIN:MODE?')!= 'AUTO'):
            scope.write('TRIGGER:MAIN:MODE AUTO')
        #self.setUpMeanCollection()
        self.scope = scope

    #prompts for current value in amps
    #saves to an array
    def collectCurrent(self):
        prompt ='Enter current value in Amps'
        current = input(prompt)
        return current
    
    #same as collectCurrent, but with the ability to reprompt when a nonnumerical 
    #value is entered for current
    def collectCurrent_Verif(self):
        prompt ='Enter current value in Amps'
        current = util.get_response(prompt)
        return current


    #collects a  data point
    #this datapoint is a signal average over self.avg_num number of values
    #the uncertainty is computes and the units are read
    #returns an array of the form [mean, uncertainty, units]
    def collectMean(self):
        mean_val = float(self.scope.query('MEASUREMENT:MEAS1:VALUE?'))
        range = float(self.scope.query('MEASUREMENT:MEAS1:VALUE?'))
        #uncertainty in mean is range / (2^1/2 * N)
        uncert = range / (np.sqrt(2) * self.num_avg)
        mean = [mean_val, uncert]
        return mean
    

    def collectUntilDone(self, time_constant):
        data = np.array([])
        while True: 
            x = self.collectCurrent_Verif()
            if (str(x) == "quit"):
                break
            #waits 5x the time constant on the lock-in before collecting a mean value 
            time.sleep(10*time_constant)
            y = self.collectMean()
            collection_point = DataPoint(x, y[0], y[1])
            data = np.append(data, collection_point)
        return data

    #prompts the user to take a calibration measurement
    #if the user chooses no either time, 0 will be returned as the calibration value
    #and the calibration value will need to be passed to the conversion function manually later on
    def collectCalibrationMeasurement(self):
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
    
    #same as collectCalibrationMeasurement, but with some input verification
    def collectCalibrationMeasurement_Verif(self):
        initial = np.array([])
        final = np.array([])
        calibration_value = np.array([])

        prompt1='First you will need to collect a calibration measurement. Type ok to continue or quit to exit.'
        p1_allowed_replies = ['ok', 'quit', 'q']
        #convert the response to all lower case to eliminate needing to check every type of capitalization
        #if the returned response is not one of these, prompt again for same question
        prompt2='Are you ready to collect the initial calibration value? Type yes to collect, quit or no to cancel'
        prompt3='Rotate halfwave plate. When ready to collect the second calibration measurement type yes to collect. Type no or quit to cancel.'
        cal_allowed_replies = ['yes', 'no', 'quit', 'y', 'n', 'q']
    
        cal_choice =  util.get_choice(p1_allowed_replies, prompt1)
        if(cal_choice == 'ok'):
            #collect the first calibration value
            reply_collect_v1 = util.get_choice(cal_allowed_replies, prompt2)
            if(reply_collect_v1 == 'y' or reply_collect_v1 == 'yes'):
                initial = self.collectMean()
                #prompt for second calibration value
                reply_collect_v2 = util.get_choice(cal_allowed_replies, prompt3)
                if(reply_collect_v2 == 'y' or reply_collect_v2 == 'yes'):
                    final = self.collectMean()
                    cal_value = final[0] - initial[0]
                    calibration_value = np.append(calibration_value, cal_value)
                    cal_error = final[1] + initial[1]
                    calibration_value = np.append(calibration_value, cal_error)
                    calibration_value = np.append(calibration_value, initial[0])
                    calibration_value = np.append(calibration_value, final[0])
        return calibration_value


    #close all the things
    def scopeClose(self):
        self.scope.close()
        self.rm.close()


    

