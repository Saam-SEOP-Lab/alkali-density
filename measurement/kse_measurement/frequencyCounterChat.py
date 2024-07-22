import numpy as np # http://www.numpy.org/
import pyvisa as visa # http://github.com/hgrecco/pyvisa
from struct import unpack
import time
from DataPoint import DataPoint
import datetime

class frequencyCounter:
    """
    DOCS TAGS GO HERE
    """
    def __init__(self, visa_address,source_channel, freqCounter=None):
        """
        DOCS FOR INIT FUNCTION
        """
        #mirroring the setup of the oscilloscope class for now
        #tbd if that is the best course of action, but at least for now we shall go with predicability over efficiency

        self.visa_address = visa_address
        self.rm = visa.ResourceManager()
        self.source_channel = source_channel
        self.freqCounter = freqCounter

    def startfrequencyCounter(self):
        """
        Connect to the frequency counter and send initialization info.

        Parameters
        ----------
        self : frequencyCounter
            frequencyCounter object used to connect to computer, send, and receive data  
        """
        # sets the freqCounter property on the frequencyCounter object to be the connection to the keysight
        freqCounter = self.rm.open_resource(self.visa_address)
        # various set up things - setting the read and write termination strings, setting the channel, reseting the instrument before starting new measurements
        freqCounter.encoding = 'latin_1'
        freqCounter.read_termination = '\n'
        freqCounter.write_termination = '\n'
        freqCounter.source_channel = 'CH1'
        freqCounter.write('*RST')
        freqCounter.write('STAT:PRES')
        freqCounter.write('*CLS')

    
    def triggerSetup(self, trig_count, trig_source, trig_slope_dir):
        cnt_cmd = 'TRIG:COUN ' + str(trig_count) #trig_count should be an int
        src_cmd = 'TRIG:SOUR ' + trig_source #options are IMM, EXT, ADV
        slp_cmd = 'TRIG:SLOP ' + trig_slope_dir #options are NEG and POS

        #now write the commands
        self.freqCounter.write(cnt_cmd)
        self.freqCounter.write(src_cmd)
        self.freqCounter.write(slp_cmd)
        
    def measurementTypeSetup(self, m_type):
        cmd = 'CONF:'+m_type #options are things like FREQ, should generally be FREQ for now
        self.freqCounter.write(cmd)

    


