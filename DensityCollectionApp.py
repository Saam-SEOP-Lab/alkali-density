#public libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import os
import pandas as pd
from datetime import datetime
import time

#my libraries
import Utilities as util
import DensityCollectionFunctions as dcf


class App(tk.Tk):
	def __init__(self):
		super().__init__()

		#need to start these out with None, so I can close the program correctly later
		self.raw_data_file = None
		self.my_scope = None
		self.current_date = datetime.today().strftime('%Y-%m-%d')

		#if it does not already exist, make the folder for the day's data collection
		self.raw_data_folder = 'Data/Density/'+self.current_date+'/'
		try: 
			os.makedirs(self.raw_data_folder)
		except FileExistsError: 
			pass # if directory already exists

		# Title, icon, size
		self.title("Alkali Density Measurement")
		self.iconbitmap('images/codemy.ico')
		self.geometry('1200x900')

		#this should connect to the oscilloscope
		self.connection_setup()

		# Create some widgets
		self.header_lbl = tk.Label(self, text="Density Measurement", font=("Ariel", 20))
		self.header_lbl.grid(row = 0, column = 0, columnspan=2, padx = 10, pady=10)		

		self.reset_btn = tk.Button(self, text="Reset for new trial", command=self.reset_for_new_collection)
		self.reset_btn.grid(row=0, column=2, padx=10, pady=10)
	
		self.quit_button = tk.Button(self, text = "Close", command=self.close)
		self.quit_button.grid(row = 0, column = 3, padx = 10, pady=10)

		self.base_folder_select_btn = tk.Button(self, text="Select Save Location", command=self.chooseBaseFolder)
		self.base_folder_select_lbl = tk.Label(self, text="Data will be saved to "+self.raw_data_folder, font=('Ariel',14))

		self.base_folder_select_btn.grid(row=1, column=0, padx = 10, pady=10)
		self.base_folder_select_lbl.grid(row=1, column=1, columnspan=3, padx = 10, pady=10)

		# Create a frame outside this function
		self.calibration_params_frame = Calibration_Parameters(self)
		self.collection_params_frame = Collection_Parameters(self)
		self.collection_module_frame = Data_Collection(self)


	def connection_setup(self):
		#some info for collecting data
		self.time_constant = 1
		self.num_points = 10
		self.scope_addr = 'USB0::0x0699::0x0368::C041014::INSTR'
		#now connect to the scope (comment out two lines below when testing w/o scope)
		self.my_scope = dcf.connectToScope(self.scope_addr)
		dcf.setUpScopeForDataCol(self.my_scope)
	

	def save_data(self):
		self.raw_data_file.close()
		#disable the current entry and submit

	#function to close the app 
	def close(self):
		if (self.raw_data_file != None):
			self.raw_data_file.close()
		if(self.my_scope != None):
			self.my_scope.close()
		self.destroy()

	
	#select the folder where all the things will get saved to
	def chooseBaseFolder(self):
		folder = filedialog.askdirectory()
		self.raw_data_folder = folder +"/"+ self.current_date +"/"
		self.base_folder_select_lbl["text"] = "Data will be saved to "+self.raw_data_folder
		try: 
			os.makedirs(self.raw_data_folder)
		except FileExistsError: 
			pass # if directory already exists
		# I want to refresh all frames after this and this is the only way I can find to maybe do that?
		self.calibration_params_frame = Calibration_Parameters(self)
		self.collection_params_frame = Collection_Parameters(self)
		self.collection_module_frame = Data_Collection(self)

	def reset_for_new_collection(self):
		#base_folder = self.raw_data_folder
		#I think I can just refresh all the modules? Maybe?
		self.calibration_params_frame = Calibration_Parameters(self)
		self.collection_params_frame = Collection_Parameters(self)
		self.collection_module_frame = Data_Collection(self)


		




#####################################################################################
# DATA COLLECTION MODULE
#####################################################################################
class Data_Collection(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		#put this on the page
		self.grid(row = 20, column=0, columnspan=4, padx=10, pady=10)

		#prep the fields for creating a data file
		self.data_folder = self.parent.raw_data_folder
		
		#create an empty data frame to save future data
		self.raw_data = pd.DataFrame({
			"Current": [],
			"Voltage": [],
			"Voltage Mean Absolute Error": [], 
			"Voltage Standard Deviation": []
		})

		#widgets 
		self.start_data_collection_button = tk.Button(self, text="Start Data Collection", command=self.collection_setup)	
		self.start_data_collection_button.grid(row =0, column = 0, padx = 10)	
		self.raw_data_loc_lbl = tk.Label(self, text="", font=("Ariel", 12))
		self.raw_data_loc_lbl.grid(row=0, column=2, columnspan=2, padx=10)

		# label for user entry field
		self.enter_current_label = tk.Label(self, text="Enter Current Value (amps)", font=("Ariel", 14))
		# user entry fields for current
		self.enter_current = tk.Entry(self)
		#self.saveCurrentCallable = partial(self.save_text_and_clear, self.enter_current)
		self.submit_button = tk.Button(self, text="Submit", command=self.save_text_and_clear)
		
		self.error_display_lbl = tk.Label(self, text="", fg="red", font=("Ariel", 17))

		self.data_display = scrolledtext.ScrolledText(self, wrap = tk.WORD, width=100, height=8)
		
		self.enter_current_label.grid(row=2, column=0, columnspan=2, padx=10)
		self.enter_current.grid(row=2, column=2, padx=10)
		self.submit_button.grid(row=2, column=3, padx=10)
		self.error_display_lbl.grid(row=3, column=0, columnspan=4, padx=10)
		self.data_display.grid(row=4, column=0, columnspan=4)

	def validate_current(self):
		val = self.enter_current.get()
		isOk = util.entry_exists_is_number(val)
		#if an invalid entry exists:
		if(isOk==False):
			## show error
			## disable submit button or discard collected data depending on when validation can happen
			## try validating on keystroke?
			self.submit_button["state"]=tk.DISABLED
			self.error_display_lbl["text"]="Current value must be a number."
		else:
			# if entry is ok, save data to csv like normal
			self.submit_button["state"]=tk.NORMAL
			self.error_display_lbl["text"]=""
		return isOk

	def collection_setup(self):
		#set up some important parameters
		self.time_constant = 1
		self.num_points = 10
		#get the most recent experiment parameters
		exp_params = self.parent.collection_params_frame.collection_params
		l = len(exp_params["Trial Number"])
		trial = "trial-"+str(exp_params["Trial Number"].values[l-1])
		cell = "cell-"+str(exp_params["Cell"].values[l-1])
		temp = "temp-"+str(exp_params["Oven Temperature"].values[l-1])
		date = str(self.parent.current_date)
		self.data_filename =  date+"_"+cell+"_"+temp+"_"+trial+".csv"
		#create empty file for data collection
		self.data_filepath = self.data_folder+self.data_filename
		(self.raw_data).to_csv(self.data_filepath, mode='a', index=False, header=True)
		#notify the user of where this data will be saved
		save_msg = "Raw Data File: "+self.data_filename
		self.raw_data_loc_lbl["text"]=save_msg

	#need to also make this one generic I think
	def clear_current_val(self, enter_current):
		self.enter_current.delete(0, 'end')

	def saveVoltageValues(self):
		#later this will run the data collection stuff for now, just give me a number
		data_point = dcf.collectDataPoint(self.num_points, 0.1, self.parent.my_scope)
		v = data_point[0]
		v_abs_mean_err = data_point[1]
		v_std_dev = data_point[2]
		return v, v_abs_mean_err, v_std_dev
	
	def save_text_and_clear(self):
		#step 0: check the value in current field is valid
		val = self.enter_current.get()
		isOK = util.entry_exists_is_number(val)
		if(isOK==False):
			self.error_display_lbl["text"]="Current value must be a number."
		else:
			self.submit_button["state"]=tk.DISABLED
			self.error_display_lbl["text"]=""
			#also need to diable the button until timeconstant*5 is over
			total_time = self.time_constant * 5
			#disable the button at the beginning of the data collection process
			#do all the data stuff
			c = self.enter_current.get()
			v1, v2, v3 = self.saveVoltageValues()
			#v1 = 0.1 
			#v2 = 0.1
			#v3 = 0.1
			new_row = pd.DataFrame({
				"Current": [c],
				"Voltage": [v1],
				"Voltage Mean Absolute Error": [v2], 
				"Voltage Standard Deviation": [v3]
			})
			new_row.to_csv(self.data_filepath, mode='a', index=False, header=False)
			text = str(c)+", "+str(v1)+", "+str(v2)+", "+str(v3)+"\n"
			self.data_display.insert(tk.END, text)
			self.raw_data = pd.concat([self.raw_data, new_row]).reset_index(drop = True)
			#enforce time constant wait
			time.sleep(total_time)
			#clear text from field
			self.enter_current.delete(0, 'end')
			#enable button again
			self.submit_button["state"]=tk.NORMAL



#####################################################################################
# DATA COLLECTION PARAMETERS
#####################################################################################
class Collection_Parameters(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		#put the module on the page
		self.grid(row=3, column=2, rowspan=11, columnspan=2, sticky=tk.N, padx=10, pady=20)
		
		#create the params file
		self.paramfilename = "Experiment_Params_" + self.parent.current_date+".csv"
		self.param_filepath = self.parent.raw_data_folder + self.paramfilename

		self.latest_collection_params = pd.DataFrame({
				"Date": [],
				"Cell": [],
				"Oven Temperature": [],
				"Laser Wavelength": [],
				"Trial Number": [], 
				"Optical Length": [],
				"Laser Power": [], 
				"Laser Temperature": [], 
				"Lock-in Sensitivity": [],
				"Calibration Factor":[],
				"Calibration Factor Error": [], 
				"Conversion Factor" : [],
				"Conversion Factor Error" : []
			})


		#widgets
		self.collection_title_lbl = tk.Label(self, text="Density Measurement Parameters", font=("Ariel", 15))
 
		self.import_params_btn = tk.Button(self, text="get params?", command=self.update_from_cal_params)

		self.cell_lbl = tk.Label(self, text="Cell ID:", font=("Ariel", 12))
		self.oven_temp_lbl = tk.Label(self, text="Oven Temperature (C):", font=("Ariel", 12)) #oven temp, in Celcius
		self.optical_len_lbl = tk.Label(self, text="Optical Path Length (cm):", font=("Ariel", 12)) #optical length, in cm
		self.laser_power_lbl = tk.Label(self, text="Laser Power (LD1 value):", font=("Ariel", 12)) #laser power on readout
		self.laser_temp_lbl = tk.Label(self, text="Laser Temperature (ACT T value):", font=("Ariel", 12)) #laser temp on readout
		self.laser_wavelen_lbl = tk.Label(self, text="Laser Wavelength (cm):", font=("Ariel", 12)) #laser wavelength, in cm
		
		self.spacer_lbl = tk.Label(self, text="\nUPDATE THE VALUES BELOW BETWEEN CALIBRATION AND COLLECTION\n", font=("Ariel", 12))
		self.lockin_sensitivity_lbl = tk.Label(self, text="Lock-in Sensitivity (Volts):", font=("Ariel", 12)) #in VOLTS. THIS IS VERY IMPORTANT
		self.trial_num_lbl = tk.Label(self, text="Trial Number:", font=("Ariel", 12))		

		self.cell_entry = tk.Entry(self, validatecommand=self.validate_cellname, validate="focusout") #optical length, in cm
		self.oven_temp_entry = tk.Entry(self, validatecommand=self.validate_oventemp, validate="focusout") #oven temp, in Celcius
		self.optical_len_entry = tk.Entry(self, validatecommand=self.validate_optlen, validate="focusout") #optical length, in cm
		self.laser_power_entry = tk.Entry(self, validatecommand=self.validate_laserpower, validate="focusout") #laser power on readout
		self.laser_temp_entry = tk.Entry(self, validatecommand=self.validate_lasertemp, validate="focusout") #laser temp on readout
		self.laser_wavelen_entry = tk.Entry(self, validatecommand=self.validate_wavelen, validate="focusout") #laser wavelength, in cm
		self.lockin_sensitivity_entry = tk.Entry(self, validatecommand=self.validate_lockin, validate="focusout") #in VOLTS. THIS IS VERY IMPORTANT
		self.trial_num_entry = tk.Entry(self, validatecommand=self.validate_trialnum, validate="focusout") 

		#error message display
		self.error_display_lbl = tk.Label(self, text="", fg="red", font=("Ariel", 17))
		#save parameters to file button
		self.save_experiment_params_btn = tk.Button(self, text="Save Experiment Parameters", command=self.save_exp_params)
		self.disp_conversion_factor_lbl = tk.Label(self, text="Conversion factor: TBD", font=("Ariel", 12))

		#format the widgets on the page
		self.collection_title_lbl.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
		self.import_params_btn.grid(row=0, column=2, columnspan=2, padx=10)
		#parameter labels (left side)
		self.cell_lbl.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.oven_temp_lbl.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.optical_len_lbl.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_power_lbl.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_temp_lbl.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_wavelen_lbl.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=10)
		##these parameters will be different between caliration and collection
		self.spacer_lbl.grid(row=7, column=0, columnspan=4, padx=10)
		self.lockin_sensitivity_lbl.grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.trial_num_lbl.grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=10)


		#parameter entry (right)
		self.cell_entry.grid(row=1, column=2, columnspan=2, padx=10)
		self.oven_temp_entry.grid(row=2, column=2, columnspan=2, padx=10)
		self.optical_len_entry.grid(row=3, column=2, columnspan=2, padx=10)
		self.laser_power_entry.grid(row=4, column=2, columnspan=2, padx=10)
		self.laser_temp_entry.grid(row=5, column=2, columnspan=2, padx=10)
		self.laser_wavelen_entry.grid(row=6, column=2, columnspan=2, padx=10)
		##these parameters will be different between caliration and collection
		self.lockin_sensitivity_entry.grid(row=8, column=2, columnspan=2, padx=10)		
		self.trial_num_entry.grid(row=9, column=2, columnspan=2, padx=10)

		# user feedback/error display
		self.error_display_lbl.grid(row = 10, column=0, columnspan=4, padx=10)

		self.save_experiment_params_btn.grid(row=11, column=0)
		self.disp_conversion_factor_lbl.grid(row=12, column=0)


####################################################################################################
#  FUNCTIONS for DATA COLLECTION PARAMETERS frame
####################################################################################################

	def checkForParamsFile(self):
		# check for existence of daily params file
		paramsFileCreated = os.path.isfile(self.param_filepath)
		## if the file does exist, load the data into self.collection_params
		if(paramsFileCreated): 
			self.collection_params = pd.read_csv(self.param_filepath)
			n = len(self.collection_params["Trial Number"])
			if (n==0):
				#case: file was created but nothing was saved
				self.trial_num=1
			else:
				#case: file was created and previous data has been collected
				self.trial_num = self.collection_params["Trial Number"].values[n-1]+1
		## if there is not a file for today's collection create one
		else: 
			#case: file was not yet created, so create it and set trial number to 1
			#create the data frame for the experiment parameters
			self.collection_params = self.latest_collection_params
			self.trial_num = 1
			self.param_file = util.createDataCSV(self.param_filepath, self.collection_params)

	def update_from_cal_params(self):
		self.checkForParamsFile()
		#this is going find the latest calibration factor and update it from there 
		#may need to figure out a better way to match cal factor to collection
		try: 
			#case: you have taken a calibration measurement right before clicking the get params button
			self.temp_cal_params = self.parent.calibration_params_frame.cal_params
			cal_params= self.temp_cal_params
		except: 
			#case: you have not taken a calibration measurement and want to use the most recent stored values
			folder = self.parent.raw_data_folder
			#since we are saving these in a predictable way, reconstruct the file name and look for it
			filename = "Calibration_" + self.parent.current_date+".csv"
			fp = folder + filename
			cal_params = pd.read_csv(fp)
			self.temp_cal_params = cal_params


		#how many calibration measurements are present?
		num_cals = len(cal_params["Cell"])
		cell = cal_params["Cell"][num_cals-1]
		oven = cal_params["Oven Temperature"][num_cals-1]
		wavelength = cal_params["Laser Wavelength"][num_cals-1]
		optical_len = cal_params["Optical Length"][num_cals-1]
		laser_power = cal_params["Laser Power"][num_cals-1]
		laser_temp = cal_params["Laser Temperature"][num_cals-1]
		cal_f = cal_params["Calibration Factor"][num_cals-1]
		cal_err = cal_params["Calibration Factor Error"][num_cals-1]

		self.latest_collection_params["Date"] = [self.parent.current_date]
		self.latest_collection_params["Cell"] = [cell]
		self.latest_collection_params["Oven Temperature"] = [oven]
		self.latest_collection_params["Laser Wavelength"] = [wavelength]
		self.latest_collection_params["Optical Length"] = [optical_len]
		self.latest_collection_params["Laser Power"] = [laser_power]
		self.latest_collection_params["Laser Temperature"] = [laser_temp]
		self.latest_collection_params["Trial Number"] = [self.trial_num]
		self.latest_collection_params["Calibration Factor"] = [cal_f]
		self.latest_collection_params["Calibration Factor Error"] = [cal_err]
	
		#populate entry fields using values above
		self.cell_entry.insert(tk.END, self.latest_collection_params["Cell"].values[0])
		self.oven_temp_entry.insert(tk.END,self.latest_collection_params["Oven Temperature"].values[0]) #oven temp, in Celcius
		self.laser_wavelen_entry.insert(tk.END, self.latest_collection_params["Laser Wavelength"].values[0]) #laser wavelength, in cm
		self.optical_len_entry.insert(tk.END, self.latest_collection_params["Optical Length"].values[0]) #optical length, in cm
		self.laser_power_entry.insert(tk.END,self.latest_collection_params["Laser Power"].values[0]) #laser power on readout
		self.laser_temp_entry.insert(tk.END, self.latest_collection_params["Laser Temperature"].values[0]) #laser temp on readout
		self.trial_num_entry.insert(tk.END, self.latest_collection_params["Trial Number"].values[0])

	def save_exp_params(self):
		#self.checkForParamsFile()
		try: 
			cal_params = self.parent.calibration_params_frame.cal_params
		except:
			cal_params = self.temp_cal_params

		num_cals = len(cal_params["Cell"])
		cal_f = float(cal_params["Calibration Factor"][num_cals-1])
		cal_error = float(cal_params["Calibration Factor Error"][num_cals-1])
		lock_in_setting = float(self.lockin_sensitivity_entry.get())
		conv_f = dcf.calculate_conversion_factor(lock_in_setting, cal_f) 
		conv_err = dcf.calculate_conversion_factor(lock_in_setting, cal_error)

		self.latest_collection_params["Trial Number"] = [self.trial_num_entry.get()]
		self.latest_collection_params["Lock-in Sensitivity"] = [lock_in_setting]
		self.latest_collection_params["Conversion Factor"] = [conv_f]
		self.latest_collection_params["Conversion Factor Error"] = [conv_err]

		self.latest_collection_params.to_csv(self.param_filepath, mode='a', index=False, header=False)
		self.collection_params = pd.concat([self.collection_params, self.latest_collection_params]).reset_index(drop = True)
		#show the calculated calibration value on screen
		conv_f_formatted = util.formatter(conv_f, 4)
		self.disp_conversion_factor_lbl["text"]="Conversion Factor: " + str(conv_f_formatted)

########### VALIDATION FUNCTIONS #######################################################	
# helper function to change the error message box so I only have to write this one time
	def err_msg_disp(self, isok):
		msg = "This field requires a numerical value"
		if(isok):
			self.error_display_lbl.config(text="")
		else: 
			self.error_display_lbl.config(text=msg)

	def validate_cellname(self):
		val = self.cell_entry.get()
		isAcceptable = util.validate_text_exists(val)
		if(isAcceptable):
			self.error_display_lbl.config(text="")
		else: self.error_display_lbl.config(text="This field cannot be blank")
		return isAcceptable

	def validate_oventemp(self):
		val = self.oven_temp_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_optlen(self):
		val = self.optical_len_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_laserpower(self):
		val = self.laser_power_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_lasertemp(self):
		val = self.laser_temp_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_wavelen(self):
		val = self.laser_wavelen_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_lockin(self):
		val = self.lockin_sensitivity_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_trialnum(self):
		val = self.trial_num_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable

############## END OF VALIDATION FUNCTIONS ################################



#####################################################################################
# CALIBRATION PARAMETERS
#####################################################################################
class Calibration_Parameters(tk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		# Put this sucker on the screen
		self.grid(row=3, column=0, rowspan=11, columnspan=2, sticky=tk.N, padx=10, pady=20)

		#create a calibration file for the day if none exists
		self.calfilename = "Calibration_" + self.parent.current_date+".csv"
		self.calibration_filepath = self.parent.raw_data_folder + self.calfilename

		#create an empty data frame to save future data
		self.latest_cal_params = pd.DataFrame({
			"Date": [],
			"Cell": [],
			"Oven Temperature": [],
			"Laser Wavelength": [],
			"Optical Length": [],
			"Laser Power": [], 
			"Laser Temperature": [], 
			"Lock-in Sensitivity": [],
			"Dial Rotation": [], 
			"Physical Rotation": [],
			"Initial Calibration Value": [],
			"Initial Calibration Error": [],
			"Final Calibration Error": [],
			"Final Calibration Error": [],
			"Calibration Factor":[],
			"Calibration Factor Error": []
		})

		self.calibration_header = tk.Label(self, text="Calibration", font=("Ariel", 15))

		# Create data field labels
		self.cell_lbl = tk.Label(self, text="Cell ID:", font=("Ariel", 12))
		self.oven_temp_lbl = tk.Label(self, text="Oven Temperature (C):", font=("Ariel", 12)) #oven temp, in Celcius
		self.optical_len_lbl = tk.Label(self, text="Optical Path Length (cm):", font=("Ariel", 12)) #optical length, in cm
		self.laser_power_lbl = tk.Label(self, text="Laser Power (LD1 value):", font=("Ariel", 12)) #laser power on readout
		self.laser_temp_lbl = tk.Label(self, text="Laser Temperature (ACT T value):", font=("Ariel", 12)) #laser temp on readout
		self.laser_wavelen_lbl = tk.Label(self, text="Laser Wavelength (cm):", font=("Ariel", 12)) #laser wavelength, in cm
		
		self.spacer_lbl = tk.Label(self, text="\nUPDATE THE VALUES BELOW BETWEEN CALIBRATION AND COLLECTION \n", font=("Ariel", 12))
		self.lockin_sensitivity_lbl = tk.Label(self, text="Lock-in Sensitivity (Volts):", font=("Ariel", 12)) #in VOLTS. THIS IS VERY IMPORTANT
		self.physical_rotation_lbl = tk.Label(self, text="Calibration Physical Rotation (Degrees):", font=("Ariel", 12)) #the angle (in degrees) rotated on the dial. Note that 1 degree = 1 rotations of the small dial

		self.cell_entry = tk.Entry(self, validatecommand=self.validate_cellname, validate="focusout") #name of cell being used
		self.oven_temp_entry = tk.Entry(self, validatecommand=self.validate_oventemp, validate="focusout") #oven temp, in Celcius
		self.optical_len_entry = tk.Entry(self, validatecommand=self.validate_optlen, validate="focusout") #optical length, in cm
		self.laser_power_entry = tk.Entry(self, validatecommand=self.validate_laserpower, validate="focusout") #laser power on readout
		self.laser_temp_entry = tk.Entry(self, validatecommand=self.validate_lasertemp, validate="focusout") #laser temp on readout
		self.laser_wavelen_entry = tk.Entry(self, validatecommand=self.validate_wavelen, validate="focusout") #laser wavelength, in cm
		self.lockin_sensitivity_entry = tk.Entry(self, validatecommand=self.validate_lockin, validate="focusout") #in VOLTS. THIS IS VERY IMPORTANT
		self.physical_rotation_entry = tk.Entry(self, validatecommand=self.validate_rotation, validate="focusout") #the angle (in degrees) rotated on the dial. Note that 1 degree = 1 rotations of the small dial

		#get the calibration values
		self.collect_cal_btn = tk.Button(self, text="Collect Initial Calibration", command=self.getCal) #initial calibration rotation value
		self.initial_cal_val_disp = tk.Label(self, text="TBD", font=("Ariel", 12)) #initial calibration rotation value
		self.final_cal_val_disp = tk.Label(self, text="TBD", font=("Ariel", 12)) #initial calibration rotation value

		#save everything to file
		self.save_params_button = tk.Button(self, text="Save Calibration", command=self.save_cal_info)
		self.display_cal_value = tk.Label(self, text="Calibration Factor: TBD",font=("Ariel", 12))	

		#error message display
		self.error_display_lbl = tk.Label(self, text="", fg="red", font=("Ariel", 17))

		#reset the calibration module to take a new calibration measurement
		self.reset_for_new_cal_btn = tk.Button(self, text="Take A New Calibration Measurement", command = self.clear_cal_info)


		#organize all the things on screen
		#header
		self.calibration_header.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
		#parameter labels (left side)
		self.cell_lbl.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.oven_temp_lbl.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.optical_len_lbl.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_power_lbl.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_temp_lbl.grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.laser_wavelen_lbl.grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=10)
		##these parameters will be different between caliration and collection
		self.spacer_lbl.grid(row=7, column=0, columnspan=4)
		self.lockin_sensitivity_lbl.grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.physical_rotation_lbl.grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=10)
		#parameter entry (right)
		self.cell_entry.grid(row=1, column=2, columnspan=2, padx=10)
		self.oven_temp_entry.grid(row=2, column=2, columnspan=2, padx=10)
		self.optical_len_entry.grid(row=3, column=2, columnspan=2, padx=10)
		self.laser_power_entry.grid(row=4, column=2, columnspan=2, padx=10)
		self.laser_temp_entry.grid(row=5, column=2, columnspan=2, padx=10)
		self.laser_wavelen_entry.grid(row=6, column=2, columnspan=2, padx=10)
		##these parameters will be different between caliration and collection
		self.lockin_sensitivity_entry.grid(row=8, column=2, columnspan=2, padx=10)
		self.physical_rotation_entry.grid(row=9, column=2, columnspan=2, padx=10)

		#user feedback - show errors for incorrect entries here
		self.error_display_lbl.grid(row=10, column=0, columnspan=4, padx=10)

		#collect calibration vals
		self.collect_cal_btn.grid(row=11, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.initial_cal_val_disp.grid(row=11, column=2, padx=10)
		self.final_cal_val_disp.grid(row=11, column=3, padx=10)
		#save all the things to a file
		self.save_params_button.grid(row=12, column=0, columnspan=2, sticky=tk.W, padx=10)
		self.display_cal_value.grid(row=12, column=2, columnspan=2, padx=10)



#####################################################################################
# FUNCTIONS for CALIBRATION PARAMETERS frame
#####################################################################################

### Surely there is a better way than doing this field by field explicitly. 
### But I can't figure out what that is. So sorry future me I guess, we're 
### validating every field individually. 

# helper function to change the error message box so I only have to write this one time
	def err_msg_disp(self, isok):
		msg = "This field requires a numerical value"
		if(isok):
			self.error_display_lbl.config(text="")
		else: 
			self.error_display_lbl.config(text=msg)

	def validate_cellname(self):
		val = self.cell_entry.get()
		isAcceptable = util.validate_text_exists(val)
		if(isAcceptable):
			self.error_display_lbl.config(text="")
		else: self.error_display_lbl.config(text="This field cannot be blank")
		return isAcceptable

	def validate_oventemp(self):
		val = self.oven_temp_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_optlen(self):
		val = self.optical_len_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_laserpower(self):
		val = self.laser_power_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_lasertemp(self):
		val = self.laser_temp_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_wavelen(self):
		val = self.laser_wavelen_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_lockin(self):
		val = self.lockin_sensitivity_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable
	
	def validate_rotation(self):
		val = self.physical_rotation_entry.get()
		isAcceptable = util.entry_exists_is_number(val)
		self.err_msg_disp(isAcceptable)
		return isAcceptable

############## END OF VALIDATION FUNCTIONS ################################

	def checkForCalFile(self):
		calFileExists = os.path.isfile(self.calibration_filepath)
		if(calFileExists):
			self.cal_params = pd.read_csv(self.calibration_filepath)
		else:
			self.cal_params = self.latest_cal_params
			self.calibration_file = util.createDataCSV(self.calibration_filepath, self.cal_params)

	def getCal(self):
		if (self.initial_cal_val_disp["text"]=="TBD"):
			self.cal1=dcf.collectDataPoint(5, 0.01, self.parent.my_scope)
			#for testing when no scope present comment above and use
			#self.cal1 = [1,0.1,0.1]
			cal_1_formmated = util.formatter(self.cal1[0], 4)
			self.initial_cal_val_disp["text"]=cal_1_formmated
		elif (self.final_cal_val_disp["text"]=="TBD"):
			self.cal2=dcf.collectDataPoint(5, 0.01, self.parent.my_scope)
			#for testing when no scope present comment above and use
			#self.cal2 = [3,0.1,0.1]
			cal_2_formmated = util.formatter(self.cal1[0], 4)
			self.final_cal_val_disp["text"]=cal_2_formmated
		else:
			print("calibration complete")

	def save_cal_info(self):
		self.checkForCalFile()
		try: 
			initcal = float(self.cal1[0])
			initcal_err = float(self.cal1[1])
			fincal = float(self.cal2[0])
			fincal_err = float(self.cal2[1])
		except:
			initcal = 0
			initcal_err = 0
			fincal = 0
			fincal_err = 0

		#calculate the conversion factor
		lockin_sens = float(self.lockin_sensitivity_entry.get())
		dial_angle = float(self.physical_rotation_entry.get())
		cal_angle = dial_angle*2
		cal_factor = dcf.calculateCalibrationFactor(lockin_sens, initcal, fincal, cal_angle)
		cal_factor_error = dcf.calculateCalibrationError(lockin_sens, initcal_err, fincal_err, cal_angle)

		new_row = pd.DataFrame({
			"Date": [self.parent.current_date],
			"Cell": [self.cell_entry.get()],
			"Oven Temperature": [self.oven_temp_entry.get()],
			"Laser Wavelength": [self.laser_wavelen_entry.get()],
			"Optical Length": [self.optical_len_entry.get()],
			"Laser Power": [self.laser_power_entry.get()], 
			"Laser Temperature": [self.laser_temp_entry.get()], 
			"Lock-in Sensitivity": [lockin_sens],
			"Dial Rotation": [dial_angle], 
			"Physical Rotation": [cal_angle],
			"Initial Calibration Value": [initcal],
			"Initial Calibration Error": [initcal_err],
			"Final Calibration Error": [fincal],
			"Final Calibration Error": [fincal_err],
			"Calibration Factor": [cal_factor],
			"Calibration Factor Error": [cal_factor_error]
			})
		new_row.to_csv(self.calibration_filepath, mode='a', index=False, header=False)
		self.cal_params = pd.concat([self.cal_params, new_row]).reset_index(drop = True)
		#show the calculated calibration value on screen
		cal_f_formatted = util.formatter(cal_factor, 4)
		self.display_cal_value["text"]="Calibration Factor: " + str(cal_f_formatted)

	def clear_cal_info():
		pass







## RUN THE APP ##
if __name__ == '__main__':
	app = App()
	app.mainloop()
	
	#app = App()
	#app.mainloop()