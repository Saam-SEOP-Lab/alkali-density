#################################################################################################
# THIS IS THE ONE THAT WORKS DO NOT DELETE
# sets up a keysight frequency counter to trigger on external voltage change
# collects data from the onboard buffer every few seconds saving to CSV file
#################################################################################################
import tkinter as tk
import threading
import nidaqmx
import time
import pyvisa as visa
import pandas as pd
import Utilities as util
from os import path
from pymeasure.instruments.keithley import Keithley2000
from pymeasure.adapters import PrologixAdapter
import numpy as np
import math




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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
 
        self.title = "Kse Data Collection"
        self.geometry('900x900')

        #collect data flag
        self.collection_active = False
        self.collection_cycle_active = None

        #Collection parameters set here:
        self.trig_count = 10
        self.trig_count_cmd = getTrigCountCmd(self.trig_count)
        self.trig_source = 'EXT'
        self.trig_source_cmd = getTrigSourceCmd(self.trig_source)
        self.high_V = 2.0
        self.low_V = 0.0
        self.high_time = 0.1
        self.low_time = 0.4
        self.how_long_collect = 120
        self.how_many_cycles = collectionTimeToNumCycles(self.how_long_collect, self.trig_count, self.low_time, self.high_time)
        self.folder = 'Data\\kseExperiment\\'

        self.keysight_addr = 'USB0::0x0957::0x1807::MY58430132::INSTR' #name/address for the keysight connected to the computer
        self.daq_path = 'Dev2/ao0' #the path to the daq
        self.dmm_addr = 'ASRL6::INSTR' #address of USB connected to computer
        self.gpib_channel_no = 1 #the channel number for the GPIB connection from the dmm. this can be set on the dmm to anything between 1 and 16

        self.start_time = None

        #widgets
        self.initialize_btn = tk.Button(self, text='Initialize data collection', command=self.setup_data_collection)
        self.initialize_btn.grid(row=0, column=0, padx=10)
        self.start_col_btn = tk.Button(self, text='Begin Data Collection', command=self.collection_thread)
        self.start_col_btn.grid(row=0, column=1, padx=10)
        self.stop_col_btn = tk.Button(self, text='Stop Data Collection', command=self.stop_collection)
        self.stop_col_btn.grid(row=0, column=2, padx=10)

        #plot widget
        #self.section_lbl = tk.Label(self, text="testing")
        #self.section_lbl.grid(row=4, column=0)
        #self.fig, self.ax = plt.subplots()
        #self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        #self.canvas_widget = self.canvas.get_tk_widget() # Convert the Figure to a tkinter widget
        #self.canvas_widget.grid(row=5, column=2, sticky='S', padx=10, pady=10) # Show the widget on the screen
        #self.canvas.draw() # Draw the graph on the canvas?

    def graphing_thread(self):
        self.t2 = threading.Thread(target=self.grapher)
        self.t2.start()

    
    def collection_thread(self):
        self.t1 = threading.Thread(target=self.collect_data)
        self.collection_active = True
        self.t1.start()

    def setup_data_collection(self):
        print('initializing data collection')

        #do all the document prep at the beginning so it doesn't slow down collection later
        #create a new csv file at the specified location
        self.filename = util.dtStringForFilename()+'.csv'
        self.fp = self.folder + self.filename
        self.file = open(self.fp, 'a')
        #create an empty data frame and save the headers to the file
        self.df_headers = pd.DataFrame({'Frequencies': [], 'Voltages': [], 'Times':[], 'Timestamps':[]})
        self.df_headers.to_csv(self.fp, mode='a', index=False)
        print('Output file created')

        # open the resource manager so we can connect to the keysight and the keithley
        self.rm = visa.ResourceManager()

        # Keysight connection setup
        self.freq_counter = self.rm.open_resource(self.keysight_addr)
        self.freq_counter.encoding = 'latin_1'
        self.freq_counter.source_channel = 'CH1'

        # Keysight data collection set up
        ## reset everything and clear the event queues
        self.freq_counter.write('*RST')
        self.freq_counter.write('STAT:PRES')
        self.freq_counter.write('*CLS')
        ## set the type of measurement to frequency
        self.freq_counter.write('CONF:FREQ')
        self.freq_counter.write(self.trig_source_cmd)
        self.freq_counter.write('TRIG:SLOP POS')
        self.freq_counter.write(self.trig_count_cmd)

        # DAQ Setup and task initialization
        self.task = nidaqmx.Task()
        self.task.ao_channels.add_ao_voltage_chan(self.daq_path)
        print('Starting Collection')
        self.task.start()
        self.task.write(0.0)#make sure we are starting at 0V

        #Keithley dmm connection set up
        self.adapter = PrologixAdapter(self.dmm_addr, self.gpib_channel_no) #create prologix adapter and connect to GPIB w/ address 1
        self.dmm = Keithley2000(self.adapter) #create the instrument using the adapter

        # Keithley data collection set up
        ## reset everything and clear the event queues
        self.dmm.reset()
        ## need to set trigger type to external
        self.dmm.write(self.trig_source_cmd)
        ## set trigger count to the desired number of datapoints per collection cycle
        self.dmm.write(self.trig_count_cmd)
        ## set sample count to 1 (this is one sample per trigger)
        self.dmm.write('SAMP:COUN 1')

    def collect_data(self):
        print('Collecting data')

        #do all the document prep at the beginning so it doesn't slow down collection later
        #create a new csv file at the specified location
        self.filename = util.dtStringForFilename()+'.csv'
        self.fp = self.folder + self.filename
        self.file = open(self.fp, 'a')
        #create an empty data frame and save the headers to the file
        self.df_headers = pd.DataFrame({'Frequencies': [], 'Voltages': [], 'Times':[], 'Timestamps':[]})
        self.df_headers.to_csv(self.fp, mode='a', index=False)
        print('Output file created')

        # open the resource manager so we can connect to the keysight and the keithley
        self.rm = visa.ResourceManager()

        # Keysight connection setup
        self.freq_counter = self.rm.open_resource(self.keysight_addr)
        self.freq_counter.encoding = 'latin_1'
        self.freq_counter.source_channel = 'CH1'

        # Keysight data collection set up
        ## reset everything and clear the event queues
        self.freq_counter.write('*RST')
        self.freq_counter.write('STAT:PRES')
        self.freq_counter.write('*CLS')
        ## set the type of measurement to frequency
        self.freq_counter.write('CONF:FREQ')
        self.freq_counter.write(self.trig_source_cmd)
        self.freq_counter.write('TRIG:SLOP POS')
        self.freq_counter.write(self.trig_count_cmd)

        # DAQ Setup and task initialization
        self.task = nidaqmx.Task()
        self.task.ao_channels.add_ao_voltage_chan(self.daq_path)
        print('Starting Collection')
        self.task.start()
        self.task.write(0.0)#make sure we are starting at 0V

        # Initialize the keysight
        #freq_counter.write('INIT')

        # Continuing the things I hate, I have to wait until after the garbage cycle completes on the keysight to set up the dmm
        # because if I don't it gets into a mystery state where it doesn't understand how to send data properly and I don't know why
        # I would like to fix this correctly by figuring out how to reliably reset the dmm to the state it is in at power up, but since I 
        # have yet to figure that out, we're doing this stupid work around
        #Keithley dmm connection set up

        self.adapter = PrologixAdapter(self.dmm_addr, self.gpib_channel_no) #create prologix adapter and connect to GPIB w/ address 1
        self.dmm = Keithley2000(self.adapter) #create the instrument using the adapter

        # Keithley data collection set up
        ## reset everything and clear the event queues
        self.dmm.reset()
        ## need to set trigger type to external
        self.dmm.write(self.trig_source_cmd)
        ## set trigger count to the desired number of datapoints per collection cycle
        self.dmm.write(self.trig_count_cmd)
        ## set sample count to 1 (this is one sample per trigger)
        self.dmm.write('SAMP:COUN 1')


        self.cycle_num=1
        while (self.collection_active):
            self.collection_cycle_active = True

            self.freq_counter.write('INIT')
            #do one trigger cycle to get rid of the empty data point that apparently gets collected for reasons?
            #I hate that this is a thing, but it appears to be a thing, so we're going to roll with it
            self.task.write(2.0)
            time.sleep(0.1)
            self.task.write(0.0)
            time.sleep(0.1)
            self.freq_counter.query('R?')#remove the empty data point from the data register, so our time stamps will match up with the frequencies collected
            
            # set up the data trace so I can get more than one mesurement when we reach the end of the collection cycle
            # I have to do this here so all the data points stay in sync because of the weird empty value the keysight likes to for it's first trigger cycle
            cmd_trace = 'TRAC:POIN ' + str(self.trig_count)
            self.dmm.write(cmd_trace)
            self.dmm.write('TRAC:FEED SENS1;FEED:CONT NEXT')
            self.dmm.write('INIT')

            print('Starting Data Collection Cycle '+str(self.cycle_num))
            self.times = [] #the timestamps will go here
            self.frequencies = []
            self.dmm_vals = []
            self.time_intervals = []
            
            #times = daqUtils.genAnalogTriggerCycle(task, trig_count, high_V, low_V, high_time, low_time)
            i=0
            while (i<self.trig_count):
                self.task.write(self.high_V) #high voltage value to send (probably stay below 5V in general)
                self.times.append(time.time())
                time.sleep(self.high_time) #how long do we want to stay at the hight voltage
                self.task.write(self.low_V) #usually this will be 0V
                time.sleep(self.low_time) #how long do we want to stay at the low voltage
                if (i==0 and self.cycle_num ==1):
                    self.start_time = self.times[0]
                self.time_intervals.append((self.times[i]-self.start_time))
                i = i+1

            print('Ending Collection Cycle '+str(self.cycle_num))

            try:
                self.frequencies = self.freq_counter.query('FETC?')
            except: 
                print('I regret to inform you that something done f*cked up with the Keysight and there is no data.')
                print('Ending data collection.')
                self.task.close()
                self.freq_counter.close()
                self.adapter.close()
                self.rm.close()

            try: 
                self.dmm_vals = self.dmm.ask('TRAC:DATA?')
            except:  
                print('I regret to inform you that something done f*cked up with the Keysight and there is no data.')
                print('Ending data collection.')
                self.task.close()
                self.freq_counter.close()
                self.adapter.close()
                self.rm.close()   

            #now I need to make the data into some sort of format that we can easily put in a text file
            self.frequencies = util.stringToPandasSeries(self.frequencies, ',')
            self.dmm_vals = util.stringToPandasSeries(self.dmm_vals, ',')
            self.hrdates, self.hrtimes = util.formatTimestampsForCSV(self.times)
            
            self.df = pd.DataFrame({
                'Frequency': self.frequencies,
                'Voltage': self.dmm_vals,
                'Time': self.hrtimes, 
                'Timestamps': self.times
            })
            self.df.to_csv(self.fp, mode='a', index=False, header=False)
            self.cycle_num = self.cycle_num+1
            self.collection_cycle_active = False

    def stop_collection(self):
        self.collection_active = False
        #close the DAQ taks
        self.task.close()
        #close the csv file
        self.file.close()
        #close the connections
        self.openres = self.rm.list_opened_resources()
        print('Closing Connection with ', self.openres)
        self.freq_counter.close()
        self.adapter.close()
        self.rm.close()
        

    def grapher(self):
        x = self.time_intervals
        y = self.frequencies.to_numpy()

        # Add x and y to lists
        #xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
        #ys.append(temp_c)

        # Limit x and y lists to 20 items
        #xs = xs[-20:]
        #ys = ys[-20:]

        # Draw x and y lists
        #self.ax.clear()
        self.ax.plot(x, y)

        # Format plot
        #plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        #plt.title('TMP102 Temperature over Time')
        #plt.ylabel('Temperature (deg C)')

        # Set up plot to call animate() function periodically
        #ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
        plt.show()
        



        
        
  


        
        
        





my_app = App()
my_app.mainloop()