#public libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import pandas as pd
from density_calculations.density_calc import convertItoB_mainroom, convertVtoRot, get_info_from_fname, get_my_data_no_file, convert_to_cm_if_needed
import numpy as np
import pandas as pd

#my libraries
#import functions.utilities as util
#import functions.density_collection_functions as dcf

#what the app needs to do
## 1. allow user to select raw data file
## 2. using the raw data file title match to the correct record in experiment params
## 3. Using the conversion factor in experiment params convert 
###     the voltage and voltage error to rotation and rotation error
## 4. Using the equation for the magnetic field of the coils convert current to mag field
## 5. plot mag field vs rotation and display best fit line
## 6. determine the density and error in density from the best fit line slope

class App(tk.Tk):
	def __init__(self):
		super().__init__()
		

		self.final_data = pd.DataFrame({'Date': [],
                        'Cell Name': [],
                        'Temperature':[],
                        'Density':[],
                        'Density Error':[], 
                        'Killian Value':[] })
		

        # Title, icon, size
		self.title("Alkali Density Analysis")
		self.iconbitmap('images/codemy.ico')
		self.geometry('1200x900')

		#add inputs for verdet constant and glass_depth
		self.verdet = 1
		self.verdet_path_len = 1
		
		#widgets
		self.header_lbl = tk.Label(self, text="Density Analysis", font=("Ariel", 20))
		self.header_lbl.grid(row = 0, column = 0, columnspan=2, padx = 10, pady=10)
		
		self.load_file_btn = tk.Button(self, text="What file?", command=self.choose_file)
		self.load_file_btn.grid(row=1, column=0, padx=10)

		#self.verdet_entry = tk.Entry(self, validatecommand=self.validate_verdet, validate="focusout")
		#self.verdet_len_entry = tk.Entry(self, validatecommand=self.validate_verdet_len, validate="focusout") 
 
		self.data_display = scrolledtext.ScrolledText(self, wrap = tk.WORD, width=150, height=30)
		self.data_display.grid(row=2, column=0, columnspan=4)

		self.analysis_section = tk.Label(self, text="Analysis", font=("Ariel", 20))
		self.analysis_section.grid(row=5, column=0, padx=10)
		self.analysis_display = scrolledtext.ScrolledText(self, wrap = tk.WORD, width=150, height=10)
		self.analysis_display.grid(row=6,column=0,padx=10)


	#we have been taking two data points at 0 field because of the current switch
	#handle this by taking the two 0 values and averagating them. Use that voltage as 0 rotation
	def getZeroRotationVoltage(self):
		# find all instances of 0 current, use those as our 0 rotation
		# if there is more than one, average the voltages at 0 current and return that 
		df = self.raw_data
		zero_index = df.loc[df["Current"] == 0].index.tolist()
		zero_vs = df["Voltage"].iloc[zero_index].to_list()
		avg_0 = np.average(zero_vs)
		return avg_0
	
	def validate_verdet(self):
		pass

		
	def createProcessedFile(self):
		self.processed_filename = self.raw_filename+"_processed.csv"
		self.processed_filepath = self.base_filepath+self.processed_filename
		#get raw data as dataframe transform voltage to rotation
		zero_rotation_voltage = self.getZeroRotationVoltage() 

		voltages = self.raw_data["Voltage"]
		voltages_mae = self.raw_data["Voltage Mean Absolute Error"]
		voltages_std = self.raw_data["Voltage Standard Deviation"]
		currents = self.raw_data["Current"]
		rotations = []
		verdet_adj_rotations=[]
		rotation_mae = []
		rotation_std = []
		mag_fields = []
		l = len(voltages)
		#convert all the voltages to rotations
		for i in range (0, l):
			r = convertVtoRot(voltages[i], zero_rotation_voltage, self.conversion_factor)
			b = convertItoB_mainroom(currents[i])
			rotations.append(r)
			#verdet_adj_rotations.append(glass_verdet_adj(self.verdet, self.verdet_path_len, r, b))
			rotation_mae.append(voltages_mae[i]*self.conversion_factor)
			rotation_std.append(voltages_std[i]*self.conversion_factor)
			mag_fields.append(convertItoB_mainroom(currents[i]))
		#convert current to magnetic field
		self.processed_data = pd.DataFrame({
			"Magnetic Field (Gauss)": mag_fields,
			"Rotation (Radians)": rotations,
			#"Verdet Adjusted Rotation (Radians)": verdet_adj_rotations,
			"Rotation Mean Absolute Error": rotation_mae, 
			"Rotation Standard Deviation": rotation_std
		})
		self.data_display.insert(tk.END, self.processed_data)
		self.processed_data.to_csv(self.processed_filepath)


	def deconstruct_filename(self):
		fn = self.raw_filename
		fn_arr = fn.split("_")
		self.date = fn_arr[0]
		self.cell_id = fn_arr[1].split("-")[1]
		self.oven_temp = fn_arr[2].split("-")[1]
		self.trial_num = fn_arr[3].split("-")[1]

	def reconstruct_basefilepath(self, arr):
		basefp = ""
		for a in arr:
			basefp = basefp+a+"/"
		return basefp
	
	def get_experiment_params(self):
		self.param_filename = "Experiment_Params_"+self.date+".csv"
		self.param_filepath = self.base_filepath+self.param_filename
		all_params = pd.read_csv(self.param_filepath)
		#find the row that matches the trial number in the filename selected 
		# filter rows based on list values
		experiment_params = all_params.loc[all_params['TrialNumber'] == int(self.trial_num)].reset_index()
		self.conversion_factor = float(experiment_params['ConversionFactor'][0])
		self.conversion_factor_err = float(experiment_params['ConversionFactorError'][0])
		self.optical_length = float(experiment_params['OpticalLength'][0])
		self.probe_beam = convert_to_cm_if_needed(float(experiment_params['LaserWavelength'][0]))
		self.D2resonance = convert_to_cm_if_needed(float(experiment_params['D2Resonance'][0]))

	def choose_file(self):
		file = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
		if file is not None:
			self.raw_data = pd.read_csv(file)
			rf = str(file).split("/")
			self.raw_filename = (rf.pop()).split(".")[0] #get last element of array, also that is removed from rf
			self.base_filepath = self.reconstruct_basefilepath(rf)
			self.deconstruct_filename()#use the file name to get info about the trial to match to the params file
			self.get_experiment_params()
			self.createProcessedFile()
			self.analyze_me()
	
	def analyze_me(self):
		#get the data from the parent (assumes that we just created a processed file)
		#get the date, cellname, and temp
		print(self.processed_filename)
		date, cellname, temp = get_info_from_fname(self.processed_filename)
		olen = self.optical_length
		wl = self.probe_beam 
		D1 = 7.948E-5
		D2 = 7.80032e-5 #this will be included in the experimental params later for now hard code
		data = self.processed_data
		self.result = get_my_data_no_file(date, cellname, temp, data, D1, D2, wl, olen)
		print(self.result)
		self.analysis_display.insert(tk.END, self.result)


	
			