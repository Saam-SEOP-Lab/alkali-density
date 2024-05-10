

class DataPoint: 
    #constructor
    #creates a new datapoint with an x value, a y value, a y error, and units for x and y
    #if no units are specified default is None
    #if no y_err is specified default is 0
    def __init__(self, x_val, y_val, y_err=0):
        self.x_val = x_val
        self.y_val = y_val
        self.y_err = y_err

    
class VoltageReading:

    #constructor
    def __init__(self, v, err):
        self.voltage = v
        self.error = err
    
