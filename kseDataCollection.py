import nidaqmx
import time
import pyvisa as visa
import pandas as pd
import Utilities as util
from os import path
from pymeasure.instruments.keithley import Keithley2000
from pymeasure.adapters import PrologixAdapter
import math
import PySimpleGUI as sp
import dataGrapher as grapher

########################################## Helper functions go here ##############################################################################
def getTrigCountCmd(num):
    trig_num_cmd = 'TRIG:COUN ' + str(num)
    return trig_num_cmd

def getTrigSourceCmd(sr):
    trig_src_cmd = 'TRIG:SOUR '+ sr
    return trig_src_cmd

def collectionTimeToNumCycles(col_time, trig_count, lowtime, hightime):
    time_per_point = lowtime + hightime
    time_per_cycle = time_per_point * trig_count
    num_cycles = col_time/time_per_cycle
    #round up, to the nearest int
    num_cycles = math.ceil(num_cycles)
    return int(num_cycles)
####################################################################################################################################################


def createDataCollectionCSV(folder):
    #do all the document prep at the beginning so it doesn't slow down collection later
    #create a new csv file at the specified location
    filename = util.dtStringForFilename()
    fp = folder + '/' + filename + '.csv'
    file = open(fp, 'a')
    #create an empty data frame and save the headers to the file
    df_headers = pd.DataFrame({'Frequencies': [], 'Voltages': [], 'Times':[], 'Timestamps':[]})
    df_headers.to_csv(fp, mode='a', index=False)
    update_message = 'Output file created at ' + fp
    return update_message, file, fp

def connectToVisaResource(fc):
    rm = visa.ResourceManager()
    # Keysight connection setup
    freq_counter = rm.open_resource(fc)
    return rm, freq_counter

def setUpFreqCounter(freq_counter, trig_source_cmd, trig_count_cmd):
    freq_counter.encoding = 'latin_1'
    freq_counter.source_channel = 'CH1'
    # Keysight data collection set up
    ## reset everything and clear the event queues
    freq_counter.write('*RST')
    freq_counter.write('STAT:PRES')
    freq_counter.write('*CLS')
    ## set the type of measurement to frequency
    freq_counter.write('CONF:FREQ')
    freq_counter.write(trig_source_cmd)
    freq_counter.write('TRIG:SLOP POS')
    freq_counter.write(trig_count_cmd)

def setUpDaqTask(task, daq_path):
    task.ao_channels.add_ao_voltage_chan(daq_path)
    print('Starting Collection')
    task.start()
    task.write(0.0)#make sure we are starting at 0V

def connectToDMM(dmm_addr, gpib_channel_no):
    adapter = PrologixAdapter(dmm_addr, gpib_channel_no) #create prologix adapter and connect to GPIB w/ address 1
    dmm = Keithley2000(adapter) #create the instrument using the adapter
    return adapter, dmm

def setUpDMM(dmm, trig_source_cmd, trig_count_cmd):
    # Keithley data collection set up
    ## reset everything and clear the event queues
    dmm.reset()
    ## need to set trigger type to external
    dmm.write(trig_source_cmd)
    ## set trigger count to the desired number of datapoints per collection cycle
    dmm.write(trig_count_cmd)
    ## set sample count to 1 (this is one sample per trigger)
    dmm.write('SAMP:COUN 1')

def tossFirstFCval(freq_counter, task):
    freq_counter.write('INIT')
    #do one trigger cycle to get rid of the empty data point that apparently gets collected for reasons?
    #I hate that this is a thing, but it appears to be a thing, so we're going to roll with it
    task.write(2.0)
    time.sleep(0.1)
    task.write(0.0)
    time.sleep(0.1)
    freq_counter.query('R?')#remove the empty data point from the data register, so our time stamps will match up with the frequencies collected

def reinitializeDMMTrace(dmm, trig_count):
    # set up the data trace so I can get more than one mesurement when we reach the end of the collection cycle
    # I have to do this here so all the data points stay in sync because of the weird empty value the keysight likes to for it's first trigger cycle
    cmd_trace = 'TRAC:POIN ' + str(trig_count)
    dmm.write(cmd_trace)
    dmm.write('TRAC:FEED SENS1;FEED:CONT NEXT')
    dmm.write('INIT')


def collectKSEData(triggerCount, colLeng, savePath):
    #print = sp.Print

######################################### Set the your collection variables here ###################################################################
#
# trig_count = the number of measurements collected before that data is offloaded to a csv file
# trig_count_cmd = a SCPI command created from the specified trigger count
# trig_source = the trigger source for the instruments. It can be IMM, EXT, BUS, etc. For this it should be EXT
# trig_source_cmd = a SCPI command created from the specified trigger source
# high_V = the high voltage value to send as a trigger from the DAQ
# low_V = the low voltage value to send as a trigger from the DAQ, this should be 0.0
# high_time = the amount of time in seconds to send the high voltage 
# low_time = the amount of time in seconds to send the low voltage 
# how_long_collec = the length of time you want to collect data for in seconds, this will be used to determine how many cycles to collect for.
# how_many_cycles = this is determined from the length of time it takes to collect one data point, and how long the user wishes to collec data for.
# folder = where do you want data files to be saved? remember to escape back slashes on windows
#
#####################################################################################################################################################
    trig_count = triggerCount
    trig_count_cmd = getTrigCountCmd(trig_count)
    trig_source = 'EXT'
    trig_source_cmd = getTrigSourceCmd(trig_source)
    high_V = 2.5
    low_V = 0.0
    high_time = 0.5
    low_time = 0.5
    how_long_collect = colLeng
    how_many_cycles = collectionTimeToNumCycles(how_long_collect, trig_count, low_time, high_time)
    folder = savePath #'Data\\kseExperiment\\'

    keysight_addr = 'USB0::0x0957::0x1807::MY58430132::INSTR' #name/address for the keysight connected to the computer
    daq_path = 'Dev2/ao0' #the path to the daq
    dmm_addr = 'ASRL6::INSTR' #address of USB connected to computer
    gpib_channel_no = 1 #the channel number for the GPIB connection from the dmm. this can be set on the dmm to anything between 1 and 16


####################################################################################################################################################
# Data Collection starts here!
####################################################################################################################################################

    print('Collecting data for '+str(how_many_cycles)+' cycles.')

    file_created_msg, file, fp = createDataCollectionCSV(folder)

    # open the resource manager so we can connect to the keysight and the keithley
    rm, freq_counter = connectToVisaResource(keysight_addr)
    setUpFreqCounter(freq_counter, trig_source_cmd, trig_source_cmd)
    

    # DAQ Setup and task initialization
    task = nidaqmx.Task()
    setUpDaqTask(task, daq_path)
 
    # Keithley dmm connection set up
    adapter, dmm = connectToDMM(dmm_addr, gpib_channel_no)

    # Keithley data collection set up
    setUpDMM(dmm, trig_source_cmd, trig_count_cmd)


    cycle_num=1

    while (cycle_num<=how_many_cycles):
        tossFirstFCval(freq_counter, task)
    
        reinitializeDMMTrace(dmm, trig_count)

        print('Starting Data Collection Cycle '+str(cycle_num))
        times = [] #the timestamps will go here
        frequencies = ''
        dmm_vals = ''
    
        i=0
        while (i<trig_count):
            task.write(high_V) #high voltage value to send (probably stay below 5V in general)
            times.append(time.time())
            time.sleep(high_time) #how long do we want to stay at the hight voltage
            task.write(low_V) #usually this will be 0V
            time.sleep(low_time) #how long do we want to stay at the low voltage
            i = i+1

        print('Ending Collection Cycle '+str(cycle_num))

        try:
            frequencies = freq_counter.query('FETC?')
        except: 
            print('I regret to inform you that something done f*cked up with the Keysight and there is no data.')
            print('Ending data collection.')
            task.close()
            freq_counter.close()
            adapter.close()
            rm.close()

        try: 
            dmm_vals = dmm.ask('TRAC:DATA?')
        except:  
            print('I regret to inform you that something done f*cked up with the Keysight and there is no data.')
            print('Ending data collection.')
            task.close()
            freq_counter.close()
            adapter.close()
            rm.close()   

        #now I need to make the data into some sort of format that we can easily put in a text file
        frequencies = util.stringToPandasSeries(frequencies, ',')
        dmm_vals = util.stringToPandasSeries(dmm_vals, ',')
        hrdates, hrtimes = util.formatTimestampsForCSV(times)
    
        df = pd.DataFrame({
            'Frequency': frequencies,
            'Voltage': dmm_vals,
            'Time': hrtimes, 
            'Timestamps': times
        })
        df.to_csv(fp, mode='a', index=False, header=False)
        cycle_num = cycle_num+1
    
    #close the DAQ taks
    task.close()
    #close the csv file
    file.close()
    #close the connections
    openres = rm.list_opened_resources()
    print('Closing Connection with ', openres)
    freq_counter.close()
    adapter.close()
    rm.close()