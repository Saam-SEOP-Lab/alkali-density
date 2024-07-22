
import datetime
import numpy as np

class CalibrationFactor: 
    """
    A class used to manage data collected for calculating a calibration factor. 

    ...

    Attributes
    ----------
    collection_date : string
        The current date. 
    cal_rot : float 
        The rotation used to collect the calibration factor, in degrees. 
    locksense : float
        The sensitivity scale if the lock-in amplifier, in volts.
        e.g. if collecting on the 200mV scale, this should be entered as 0.002
    init_v : float
        The initial voltage reading from the oscilloscope. 
    init_v_err : float
        The error in the initial voltage reading from the oscilloscope. 
    fin_v : float
        The final voltage reading from the oscilloscope. 
    fin_v_err : float
        The error in the final voltage reading from the oscilloscope. 
    wl : float
        The wavelength of the probe laser, in cm. 
    ol : float
        The length of the path of the laser through the cell, in cm. 
    ot : float
        The oven temperature, in Celcius.
    lp : float
        The laser power, as read from the laser control box. 
    lt : float
        The laser temperature, as read from the laser control box. 

    Methods
    -------
    __init__(self, cal_rot, locksense, init_v, init_v_err, fin_v, fin_v_err, wl, ol, ot, lp, lt)
        Creates a CalibrationFactor object.
    """
    #constructor
    #creates a new calibration factor object
    def __init__(self, cal_rot, locksense, init_v, init_v_err, fin_v, fin_v_err, wl, ol, ot, lp, lt):
        """
        Creates a CalibrationFactor object.

        Parameters
        ----------
        self : CalibrationFactor
            the CalibrationFactor object to be created. 
        cal_rot : float 
            The rotation used to collect the calibration factor, in degrees. 
        locksense : float
            The sensitivity scale if the lock-in amplifier, in volts.
            e.g. if collecting on the 200mV scale, this should be entered as 0.002
        init_v : float
            The initial voltage reading from the oscilloscope. 
        init_v_err : float
            The error in the initial voltage reading from the oscilloscope. 
        fin_v : float
            The final voltage reading from the oscilloscope. 
        fin_v_err : float
            The error in the final voltage reading from the oscilloscope. 
        calibration_factor : 
            The calibration to use for converting voltage data to rotation data. 
        calibration_factor_err : 
            The error in the calibration factor. 
        wl : float
            The wavelength of the probe laser, in cm. 
        ol : float
            The length of the path of the laser through the cell, in cm. 
        ot : float
            The oven temperature, in Celcius.
        lp : float
            The laser power, as read from the laser control box. 
        lt : float
            The laser temperature, as read from the laser control box. 

        Returns
        -------
        CalibrationFactor
            Returns a new CalibrationFactor object.  
        """

        self.collection_date = str(datetime.datetime.now())
        
        self.cal_rotation = cal_rot
        self.lockin_sensitivity = locksense #this must be in volts

        self.initial_voltage = init_v
        self.initial_voltage_err = init_v_err
        self.final_voltage = fin_v
        self.final_voltage_err = fin_v_err

        self.calibration_factor = self.calculateCalFactor(self.lockin_sensitivity, self.initial_voltage, self.final_voltage, self.cal_rotation)
        self.calibration_factor_err = self.calculateCalFactorError(self.lockin_sensitivity, self.initial_voltage_err, self.final_voltage_err)

        self.laserWavelength = wl
        self.opticalLength = ol
        self.ovenTemp = ot
        self.laserPower = lp
        self.laserTemp = lt



    def calculateCalFactor(self, scale, v_i, v_f, angle):
        """
        Calculates the value of a CalibrationFactor object.

        Parameters
        ----------
        self : CalibrationFactor
            the CalibrationFactor object to be manipulated. 
        scale : float
        v_i : float
            The initial voltage reading. 
        v_f : float
            The final voltage reading.
        angle : float
            The calibration angle in degrees. 

        Returns
        -------
        convsersion_factor : float
            Returns the value of the conversion factor.  
        """

        #calculate scaling factor from lockin sensitivity
        scaled_init = (scale * v_i) / 10
        scaled_final = (scale * v_f) / 10
        scaled_diff = abs(scaled_final - scaled_init)
        convsersion_factor = (angle * np.pi)/(180 * scaled_diff)
        return convsersion_factor
    
    def calculateCalFactorError(self, scale, v_i_err, v_f_err):
        """
        Calculates the total error in the conversion factor. 

        Parameters
        ----------
        self : CalibrationFactor
            the CalibrationFactor object to be manipulated. 
        scale : float
        v_i_err : float
            The initial voltage reading error. 
        v_f_err : float
            The final voltage reading error.
        
        Returns
        -------
        convsersion_factor : float
            Returns the value of the conversion factor error.  
        """

        total_V_err = scale * (abs(v_i_err) + abs(v_f_err))
        return total_V_err
    
    def calFPrepforJSON(self):
        """
        Formats the calibration factor data to be saved to a JSON file.

        Parameters
        ----------
        self : CalibrationFactor
            the CalibrationFactor object to be manipulated. 
        
        Returns
        -------
        calibrationInfoJSON : dictionary
            A dictionary object to be saved to a JSON file.  
        """

        calibrationInfoJSON = {
            "dateCollected": self.collection_date,
            "calibrationRotation": self.cal_rotation,
            "lockinSensitivity": self.lockin_sensitivity,
            "initialVoltage": self.initial_voltage, 
            "initialVoltageError": self.initial_voltage_err,
            "finalVoltage": self.final_voltage,
            "finalVoltageError": self.final_voltage_err,
            "calibrationFactor": self.calibration_factor,
            "calibrationFactorError": self.calibration_factor_err,
            "laserWavelength": self.laserWavelength,
            "opticalLength": self.opticalLength,
            "ovenTemp": self.ovenTemp,
            "laserPower": self.laserPower,
            "laserTemp": self.laserTemp        
        }
        return calibrationInfoJSON





