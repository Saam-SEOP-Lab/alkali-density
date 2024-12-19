import csv
import pandas as pd

from functions.formatting import dtStringForFilename, timestampToArray
from functions.formatting import formatter
from functions.fitting_and_error import linear_fit_data_with_error, get_error_from_covar
from functions.alkali_density_calculation import rb_density_first_order, rb_density_second_order, rb_density_third_order, killian_density, glass_verdet_adj


def exportToCSV(fp, fields, formatted_data):
    """
    Exports the provided data to a csv file. 
    
    Parameters
    ----------
    fp : string
        location to save the data to, as a string.
    fields : array of strings
        the headers for the csv as an array. 
    formatted_data : 2D array 
        the data to save to the csv file as two dimensional array. 
    """

    filename = str(fp)
    #first check that no files with the same name exist
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(fields)
        # writing the data rows
        csvwriter.writerows(formatted_data)   

def createFilePath(folder, collection_type):
    filename = collection_type + dtStringForFilename()
    fp = folder + filename
    return fp

def createDataCSV(fp, empty_dataframe):
    file = open(fp, 'a')
    empty_dataframe.to_csv(fp, mode='a', index=False)
    return file

def createDataCSV_Indexed(fp, empty_dataframe):
    file = open(fp, 'a')
    empty_dataframe.to_csv(fp, mode='a', index=True)
    return file

def createParamsCSV(fp, params):
    file = open(fp, 'w')
    params.to_csv(fp, mode='w', index=False)
    file.close()

#takes an array of timestamps and converts it to two arrays, one containing all the dates, the other containing all the times
def formatTimestampsForCSV(times):
    arry_0 = []
    arry_1 = []

    for x in times:
        temp = timestampToArray(x)
        arry_0.append(temp[0])
        arry_1.append(temp[1])
    
    return (arry_0, arry_1)

def get_processed_data_from_csv(fp):
    """
    Returns density data in a csv file as a set of arrays. 
    
    Parameters
    ----------
    fp : string
        The file path to the file containing the target data. 

    Returns
    -------
    magnetic_fields : array 
        An array of float values representing the magnetic field values used in the experiment. 
    rotation_vals : array 
        An array of float values representing the rotation field values found in the experiment. 
    rotation_MAE : array 
        An array of float values representing the mean average error of the rotation values found in the experiment. 
    rotation_STD : array 
        An array of float values representing the standard deviations of the rotation values found in the experiment. 
    """
    processed_data = pd.read_csv(fp)
    # Convert each column of the dataframe into a numpy array
    magnetic_fields = processed_data["Magnetic Field (Gauss)"].to_numpy()
    rotation_vals = processed_data["Rotation (Radians)"].to_numpy()
    rotation_MAE = processed_data["Rotation Mean Absolute Error"].to_numpy()
    rotation_STD = processed_data["Rotation Standard Deviation"].to_numpy()

    return magnetic_fields, rotation_vals, rotation_MAE, rotation_STD

def get_info_from_fname(processed_filepath):
    """
    Takes the file path to a processed faraday rotation data set and returns the experiment parameters associated with that file.
    
    Parameters
    ----------
    processed_filepath : string
        The file path to the file containing the target data. 

    Returns
    -------
    col_date : string 
        The collection date of the experiment. 
    cell_name : string 
        The id of the cell used in the experiment. 
    temperature : string 
        The oven temperature, in Celsius, used for the experiment. 
    """
    #split the file path by / 
    fp_ary = str(processed_filepath).split('/')
    #take the last element of the array to get the file name
    #split that on . to separate extension from rest of name
    properties = fp_ary[-1].split('.')[0].split('_')
    #need to get the following params from the 
    col_date = properties[0]
    cell_name = properties[1].split('-')[1]
    temperature = properties[2].split('-')[1]
    return col_date, cell_name, temperature

#TODO - rename this function
def get_my_data_no_file(date, cellname, temp, data, d1_res, d2_res, wavelength, optical_path, isPositive, verdet_adjustment):
    """
    Calculates the alkali metal density, including the paramagnetic correction term. See Vleigen et al (2001), DOI: 10.1016/S0168-9002(00)01061-5 equations 1 and 3, for the approximate form of this equation, though note that Vleigen's first term is incorrect. 
    All values are in cgs units.        

    Parameters
    ----------
    date : string
        The date on which the experiment was performed. 
    cell_name : string 
        The ID of the cell used for the experiment. 
    temp : float
        Temperature of the oven.  
        Units: Celsius (note that the function will convert to kelvin) 
    data : 
        A DataFrame object containing the magnetic field, rotation, and rotation standard deviation data. 
    d1_res : float
        D1 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    d2_res : float
        D2 transition resonance wavelength for the alkali metal and cell used. 
        Units: cm
    wavelength : float
        Wavelength of the probe beam used.  
        Units: cm
    optical_path : float
        Path length traveled through the cell by the probe beam. 
        Units: cm
    isPositive :  boolean   
        A boolean value indicating whether the paramagnetic correction term should be positive or negative. 
    verdet_adjustment : float
        The value used to adjust the rotation data to account for the Verdet effect. 

    Returns
    -------
    output : DataFrame
        A DataFrame containing the experimental data formatted for further analysis. 
    """

    collected_date = date
    cell = cellname
    tmp = float(temp)
    b_field = data["Magnetic Field (Gauss)"]
    rot = data["Rotation (Radians)"]
    r_err_STD = data["Rotation Standard Deviation"]
    wl_err = 3E-10
    f = .667 #ocillator strength
    k = 7/6 #kappa
    line_wid = 3e9 #line width (Hz)
    T_d = 34e-13 #T_d from romalis (s)

    #get density without verdet adjustment
    fit_params_0, cov_0 = linear_fit_data_with_error(b_field, rot, r_err_STD)
    slope_0 = fit_params_0[0]
    cov_err_0 = get_error_from_covar(cov_0)
    uncorrected_density = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, slope_0)
    uncorrected_density_err = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, cov_err_0)

    #adjust rotations using verdet constant of glass
    rot_adj = glass_verdet_adj(verdet_adjustment, rot, b_field)

    fit_params, cov = linear_fit_data_with_error(b_field, rot_adj,r_err_STD)
    slope = fit_params[0]
    cov_err = get_error_from_covar(cov)

    FO_density = rb_density_first_order(d1_res, d2_res, optical_path, wavelength, slope)
    FO_density_error = rb_density_first_order(d1_res, d2_res, optical_path, wavelength, cov_err)
    SO_density = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, slope)
    SO_density_error = rb_density_second_order(d1_res, d2_res, optical_path, wavelength, tmp, cov_err)
    TO_density = rb_density_third_order(d1_res, d2_res, optical_path, wavelength, tmp, f, line_wid, k, T_d, slope)
    TO_density_error = rb_density_third_order(d1_res, d2_res, optical_path, wavelength, tmp, f, line_wid, k, T_d, cov_err)
    ### KILLIAN DENSITY
    killian_val = formatter(killian_density(tmp),4)

    #create my data frame
    output = pd.DataFrame({'Date': [collected_date],
                        'Cell Name': [cell],
                        'Temperature':[tmp],
                        'Uncorrected Density': [formatter(uncorrected_density,6)],
                        'Uncorrected Density Error': [formatter(uncorrected_density_err,6)],
                        'First Order Density':[formatter(FO_density, 6)],
                        'FO Density Error':[formatter(FO_density_error, 6)],
                        'Second Order Density': [formatter(SO_density, 6)],
                        'SO Density Error': [formatter(SO_density_error, 6)],
                        'Third Order Density': [formatter(TO_density, 6)],
                        'TO Density Error': [formatter(TO_density_error, 6)],
                        'Killian Value':[killian_val],
                        'D1 Resonance':[formatter(d1_res,5)],
                        'D2 Resonance':[formatter(d2_res,5)],
                        'Probe Beam':[formatter(wavelength, 5)]})
    return output

#Functions for data processing go here for now

#Get data from specified file
def get_plot_data(file, T):
    """
    Returns the density data from a specific file, to be used in finding the true density from the parabolic fit. 
    
    Parameters
    ----------
    file : string
        The file path to the file containing the target data.
    T : int
        An integer value for the temperature of the oven in the target experiment.  

    Returns
    -------
    killian_density : array 
        An array of the density values as calculated by Killian's equation as floats. 
    paramag_density : array 
        An array of the density values as calculated using the density equation including the paramagnetic term. 
    paramag_density_error : array 
        An array of the errors corresponding to density values as calculated using the density equation including the paramagnetic term. 
    probe_beam : array 
        An array of the probe beam wavelengths.  
    """
    data_unsorted = pd.read_csv(file)
    data = data_unsorted.sort_values('Probe Beam')
    killian_density = data.loc[data['Temperature']== T, 'Killian Value']
    paramag_density = data.loc[data['Temperature']== T, 'Density (with Paramagentic term)'].to_numpy()
    paramag_density_error = data.loc[data['Temperature']== T, 'Density Error (with Paramagentic term)'].to_numpy()
    probe_beam = data.loc[data['Temperature']== T, 'Probe Beam'].to_numpy()
    return killian_density, paramag_density, paramag_density_error, probe_beam