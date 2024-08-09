import numpy as np # http://www.numpy.org/
import pyvisa as visa # http://github.com/hgrecco/pyvisa
from struct import unpack
import time
from ZZ_depricated_remove_eventually.DataPoint import DataPoint
import datetime
import ZZ_depricated_remove_eventually.Utilities as util



class Oscope: 
    """
    A class used manage the connection between the computer and the oscilloscope. 

    ...

    Attributes
    ----------
        visa_address : string
            the NI visa address for the oscilloscope. 
        rm : object 
            the resource manager for the oscilloscope. 
        encoding : string
            The encoding to use, currently hard coded to 'latin_1'
        read_termination : string
            The read termination character to use, currently hard coded to '\n'
        write_termination : string
            The write termination character to use, currently hard coded to '\n'
        num_avg : string 
            the number of individual readings to average when collecting a data point. 
        source_channel : string  
            the channel from which data will be read (typically 'CH1' or 'CH2').
        scope : Oscope 
            an Oscope object, set to None by default. 

    Methods
    -------
    __init__(self, visa_address,num_avg,source_channel, scope=None)
        Creates a scope object.
    startScope(self)
        Connect to the oscilloscope and send initialization info.
    def collectionSetUp(self)
        Sets the following parameters necessary for data collection from the oscilloscpe:
            channel to read as channel 1,  
            datawidth to 1 
            encoding to binary
            number to of points to average to specified value
    collectCurrent(self)
        Prompts the user to enter a current value in amps and returns the resulting value
    setMeasurementTypeCommand(self, type)
        Constructs a measurement command to set the measurement type on the oscilloscope.
    getMeasurementValCommand(self)
        Constructs a measurement query to obtain the measurement value from the oscilloscope.
    collectMean(self, N)
        Collects a number of measurements equal to the set_size variable, averages them and takes the standard deviation.
    collectVoltage(self)
        Collects a voltage reading and the time at which that measurement was collected.
    collectUntilDone(self, time_constant)
        Prompts user to enter current value or quit, and records current and corresponding voltages in an array. 
        Additionally this function enforces a wait time of 5x the time constant between measurements. 
    collectCalibrationMeasurement(self)
        Collects a calibration measurement by prompting the user to take two voltage readings at a known phase shift.
    isConnectionOpen(self)
        Checks for an open connection to the oscilloscope. 
    scopeClose(self)
        Closes the connection to the oscilloscope.
    """

    def __init__(self, visa_address,num_avg,source_channel, scope=None):
        """
        Creates a scope object.

        Parameters
        ----------
        self : scope
            Scope object used to connect to computer, send, and receive data
        visa_address : string
            the NI Visa address for the device.
        num_avg : int
            the number of data points to average if taking an average.
        souce_channel : string
            the channel from which data will be read (typically 'CH1' or 'CH2').
        scope : Oscope
            an Oscope object, set to None by default. 

        Returns
        -------
        scope
            Returns a new scope object, now with active connection to the computer.  
        """
        self.visa_address = visa_address
        self.rm = visa.ResourceManager()
        self.encoding = 'latin_1'
        self.read_termination = '\n'
        self.write_termination = '\n'
        self.num_avg = num_avg
        self.source_channel = source_channel
        self.scope = scope

    def startScope(self):
        """
        Connect to the oscilloscope and send initialization info.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data  
        """

        scope = self.scope
        scope = self.rm.open_resource(self.visa_address)
        scope.timeout = 5000 # ms
        scope.encoding = 'latin_1'
        scope.read_termination = '\n'
        scope.write_termination = '\n'#None
        scope.write('*cls') # clear ESR
        self.scope = scope

    def collectionSetUp(self):
        """
        Sets the following parameters necessary for data collection from the oscilloscpe:
            channel to read as channel 1,  
            datawidth to 1 
            encoding to binary
            number to of points to average to specified value

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data
  
        """

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

    def collectCurrent(self):
        """
        Prompts the user to enter a current value in amps and returns the resulting value

        Parameters
        ----------
        self : Oscope
            Ocope object used to connect to computer, send, and receive data.

        Returns
        -------
        current : float
            The current (in amps) in the electromagnet. 
        """
        prompt ='Enter current value in Amps'
        current = input(prompt)
        return current

    def setMeasurementTypeCommand(self, type):
        """
        Constructs a measurement command to set the measurement type on the oscilloscope.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        type : string
            the type of measurement to collect (per the tektronics programming manual).

        Returns
        -------
        m_type_cmd : string
            The command to set the measurement type to the type specified. 
        """

        #construct the command
        m_type_cmd = 'MEASUREMENT:IMMED'+':TYPE '+str(type)
        return m_type_cmd
    
    def getMeasurementValCommand(self):
        """
        Constructs a measurement query to obtain the measurement value from the oscilloscope.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        
        Returns
        -------
        m_val_cmd : string
            The query to obtain the measurement value stored on the oscilloscope. 
        """

        #construct the command
        m_val_cmd = 'MEASUrement:IMMed:VALue?'
        return m_val_cmd
    
    def collectMean(self, N):
        """
        Collects a number of measurements equal to the set_size variable, averages them and takes the standard deviation.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        
        Returns
        -------
        mean : array
            Contains the mean and standard deviation of the data set. Format is [mean, std_dev] 
        """
        #how many points do we want to measure?
        set_size = N

        #create an array of 0's so I can collect a several values at one current value then average
        data_point = np.zeros(set_size)

        #set measurement type to mean
        set_type_mean = self.setMeasurementTypeCommand('MEAN')
        self.scope.write(set_type_mean)
        #set source to collect from
        self.scope.write('MEASUREMENT:IMMED:SOURCE CH1')
        collect_mean = self.getMeasurementValCommand()

        #put the values into the array so we can calculate the mean and standard dev
        for i in range(0,set_size):
            data_point[i] = float(self.scope.query(collect_mean))

        mean_val = np.average(data_point)
        #calculate standard dev of dataset 
        uncert = util.meanAbsError(data_point)#np.std(data_point)
        #create 2 element array with mean value and standard deviation for that point
        mean = [mean_val, uncert]
        #print the datapoint for now as a sanity check - REMOVE THIS?
        #print(mean)
        return mean
    
    #TODO: see if I can get time from scope rather than the computer as it would probably be more accurate
    def collectVoltage(self):
        """
        Collects a voltage reading and the time at which that measurement was collected.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        
        Returns
        -------
        data_point : array
            Contains the voltage read from the oscilloscope and time it was collected. Format is [voltage, datetime] 
        """
        #how many points do we want to measure?

        #create an array of 0's so I can collect a several values at one current value then average
        data_point = np.array([])

        #set measurement type to mean
        set_type_mean = self.setMeasurementTypeCommand('MEAN')
        self.scope.write(set_type_mean)
        #set source to collect from
        self.scope.write('MEASUREMENT:IMMED:SOURCE CH1')
        collect_mean = self.getMeasurementValCommand()

        #get timestamp for collection
        dp_collection_time = time.time()

        #put the values into the array so we can calculate the mean and standard dev
        data_point = np.append(data_point, float(self.scope.query(collect_mean)))
        data_point = np.append(data_point, str(dp_collection_time))

        return data_point
    

    def collectUntilDone(self, time_constant):
        """
        Prompts user to enter current value or quit, and records current and corresponding voltages in an array. 
        Additionally this function enforces a wait time of 5x the time constant between measurements. 

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        time_constant : int
            The time constant as set on the lock-in amplifier. 
        
        Returns
        -------
        data : numpy array
            The output array contains the average voltage from the oscilloscope, 
            and the standard deviation for the mean.
        """

        print("Beginning data collection.")
        data = np.array([])
        N = 20
        while True: 
            x = self.collectCurrent()
            if (str(x) == "quit"):
                break
            #waits 5x the time constant on the lock-in before collecting a mean value 
            time.sleep(5*time_constant)
            y = self.collectMean(N)
            collection_point = DataPoint(x, y[0], y[1])
            data = np.append(data, collection_point)
        print("Data collection complete")
        return data

    
    def collectCalibrationMeasurement(self):
        """
        Collects a calibration measurement by prompting the user to take two voltage readings at a known phase shift.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        
        Returns
        -------
        calibration_value : numpy array
            Calibration factor array. Format is [inital_value, final_value] 
        """

        initial = np.array([])
        final = np.array([])
        calibration_value = np.array([])
        N = 20
        #collect the unrotated value
        prompt_collectPreRotation = 'Begining calibration process. Enter y to collect first measurement.'
        reply_collectPreRotation = input(prompt_collectPreRotation)
        if(reply_collectPreRotation == 'y'):
            initial = self.collectMean(N)
            prompt_collectPostRotation = 'Rotate the halfwave plate one degree (4 turns on the small knob). When completed enter y to collect rotated value'
            reply_collectPostRotation = input(prompt_collectPostRotation)
            if(reply_collectPostRotation == 'y'):
                final = self.collectMean(N)
                calibration_value = np.append(calibration_value, initial)
                calibration_value = np.append(calibration_value, final)
            #TODO: add else or if else to handle mistypes
        return calibration_value
    
    
    def isConnectionOpen(self):
        """
        Checks for an open connection to the oscilloscope. 

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data

        Returns
        -------
        sessionID : string
            If an active session exists, the session ID is returned. 
            If there is no active session 'No Active Session' is returned.  
        """

        try: 
            sessionID = self.scope.session
        except:
            sessionID = 'No Active Session'
        return sessionID


    def scopeClose(self):
        """
        Closes the connection to the oscilloscope.

        Parameters
        ----------
        self : Oscope
            Oscope object used to connect to computer, send, and receive data.
        """
        self.scope.close()
        self.rm.close()


    

