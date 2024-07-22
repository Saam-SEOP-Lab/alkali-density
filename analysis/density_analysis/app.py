#public libraries
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
import os
import pandas as pd
from datetime import datetime
import time

#my libraries
#import functions.utilities as util
#import functions.density_collection_functions as dcf


class App(tk.Tk):
	def __init__(self):
		super().__init__()
		
        # Title, icon, size
		self.title("Alkali Density Analysis")
		self.iconbitmap('images/codemy.ico')
		self.geometry('1200x900')
		
		#widgets
		self.header_lbl = tk.Label(self, text="Density Analysis", font=("Ariel", 20))
		self.header_lbl.grid(row = 0, column = 0, columnspan=2, padx = 10, pady=10)
		
		self.load_file_btn = tk.Button(self, text="What file?", command=self.choose_file)
		self.load_file_btn.grid(row=1, column=0, padx=10)
		

	def deconstruct_filename(self):
		fn = self.raw_filename
		fn_arr = fn.split("_")
		self.date = fn_arr[0]
		self.cell_id = fn_arr[1].split("-")[1]
		self.oven_temp = fn_arr[2].split("-")[1]
		self.trial_num = fn_arr[3].split(".")[0].split("-")[1]

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
		print(self.conversion_factor)
		print(self.conversion_factor_err)


	def choose_file(self):
		file = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
		if file is not None:
			self.raw_data = pd.read_csv(file)
			rf = str(file).split("/")
			self.raw_filename = rf.pop() #get last element of array, also that is removed from rf
			self.base_filepath = self.reconstruct_basefilepath(rf)
			self.deconstruct_filename()#use the file name to get info about the trial to match to the params file
			self.get_experiment_params()


		

	
			