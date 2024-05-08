
import datetime
import numpy as np

class CalibrationFactor: 
    #constructor
    #creates a new calibration factor object
    def __init__(self, cal_rot, locksense, init_v, init_v_err, fin_v, fin_v_err, wl, ol, ot, lp, lt):
        self.collection_date = str(datetime.datetime.now())
        
        self.cal_rotation = cal_rot
        self.lockin_sensitivity = locksense #this must be in volts
        self.scale_factor = 10/locksense

        self.initial_voltage = init_v
        self.initial_voltage_err = init_v_err
        self.final_voltage = fin_v
        self.final_voltage_err = fin_v_err

        self.calibration_factor = self.calculateCalFactor(self.scale_factor, init_v, fin_v, cal_rot)
        self.calibration_factor_err = self.calculateCalFactorError(self.scale_factor, init_v_err, fin_v_err)

        self.laserWavelength = wl
        self.opticalLength = ol
        self.ovenTemp = ot
        self.laserPower = lp
        self.laserTemp = lt
    
    def calculateCalFactor(self, scale, v_i, v_f, angle):
        #calculate scaling factor from lockin sensitivity
        scaled_init = abs(scale * v_i)
        scaled_final = abs(scale * v_f)
        scaled_diff = scaled_final - scaled_init
        convsersion_factor = angle * np.pi / (180 * scaled_diff)
        return convsersion_factor
    
    def calculateCalFactorError(self, scale, v_i_err, v_f_err):
        total_V_err = scale * (abs(v_i_err) + abs(v_f_err))
        return total_V_err
    
    def calFPrepforJSON(self):
        calibrationInfoJSON = {
            "dateCollected": self.collection_date,
            "calibrationRotation": self.cal_rotation,
            "lockinSensitivity": self.lockin_sensitivity,
            "scaleFactor": self.scale_factor,
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





