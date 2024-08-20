#public libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
from density_calculations.density_calc import convertItoB_mainroom, convertVtoRot, glass_verdet_adj
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

		

		#self.plot_lbl = tk.Label(self, text="Plot of Magnetic Field vs Rotation")
		#self.plot_disp = ""		
		#code for a generic plot - update this later 
		#f = Figure(figsize=(5,5), dpi=100)
		#a = f.add_subplot(111)
		#a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
		#canvas = FigureCanvasTkAgg(f, self)
		#canvas.get_tk_widget().grid(row=2, column=0, columnspan=4)
		#toolbar = NavigationToolbar2Tk(canvas, self)
		#toolbar.update()
		#canvas._tkcanvas.grid(row=3, column=0, columnspan=4)

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
		print(voltages)
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
		experiment_params = all_params.loc[all_params['Trial Number'] == int(self.trial_num)].reset_index()
		self.conversion_factor = float(experiment_params['Conversion Factor'][0])
		self.conversion_factor_err = float(experiment_params['Conversion Factor Error'][0])


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

	


		

	
			