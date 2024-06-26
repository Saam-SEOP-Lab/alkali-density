import numpy as np
import pandas as pd
import csv

#TODO#
# subtract initial DMM voltage from all other points to get Delta V before 


########## USEFUL CONTSANTS ######

rb87_gyromagnetic_ratio_HE = -687948.167 #Hz/Gauss
rb85_gyromagnetic_ratio_HE = -447338.733 #Hz/Gauss
cs133_gyromagnetic_ratio_HE = -344814.813 #Hz/Gauss

rb87_gyromagnetic_ratio_LE = -711218.443 #Hz/Gauss
rb85_gyromagnetic_ratio_LE = -486146.856 #Hz/Gauss
cs133_gyromagnetic_ratio_LE = -354909.377 #Hz/Gauss


conv_fact_V = 0.1 #Volts
conv_fact_G = 0.01 #Gauss
B_field_gain = 1/100

##################################


def getTimeIntervals(times):
    #convert the timestamp column into change in time, setting the first point at t=0
    #this should return an array of the same length as the provided times array, but starting at 0s
    i = 0
    delta_t = []
    for t in times:
        delta_t.append(times[i] - times[0])
        i = i+1
    return delta_t

def getMagetometerConversionFactor(volts, gauss, gain):
    mag_conversion_factor = (gauss/volts)*gain
    return mag_conversion_factor

def getVoltstoHzConversion(metal, energy):
    # Metal: enter "rb87", "rb85", or "cs133" depending on alkali metal used
    # Energy: enter "high" or "low"
    m_conv_f = getMagetometerConversionFactor(conv_fact_V, conv_fact_G, B_field_gain)
    overall_conversion_factor = 0
    if (energy == "low"):
        if (metal=="rb87"):
            overall_conversion_factor = m_conv_f*rb87_gyromagnetic_ratio_LE
        elif (metal=="rb85"):
            overall_conversion_factor = m_conv_f*rb85_gyromagnetic_ratio_LE
        elif (metal=="cs133"):
            overall_conversion_factor = m_conv_f*cs133_gyromagnetic_ratio_LE
    elif(energy == "high"):
        if (metal=="rb87"):
            overall_conversion_factor = m_conv_f*rb87_gyromagnetic_ratio_HE
        elif (metal=="rb85"):
            overall_conversion_factor = m_conv_f*rb85_gyromagnetic_ratio_HE
        elif (metal=="cs133"):
            overall_conversion_factor = m_conv_f*cs133_gyromagnetic_ratio_HE

    return overall_conversion_factor  

def getDMMChangeInVoltage(voltages):
    l = len(voltages)
    delta_Vs = []
    initial_V = float(voltages[0])
    for i in range(0,l):
        delta_Vs[i] = float(voltages[i])-initial_V
    return delta_Vs

def convertDMMData(volts, metal, energy):
    dmm_freqs = []
    convf = getVoltstoHzConversion(metal, energy)
    initial_V = float(volts[0])
    for v in volts:
        delta_V = float(v)-initial_V #convert raw voltage to change in voltage
        dmm_freqs.append(delta_V*convf) #convert change in voltage to frequency value and add to array
    return dmm_freqs

def getRawDataFromCSV(fp):
    data = csv.reader(open(fp, 'r'), delimiter=",", quotechar='|')
    freq_counter, dmm, timestamps = [], [], []

    for row in data:
        freq_counter.extend([row[0]])
        dmm.extend([row[1]])
        timestamps.extend([row[3]])

    freq_counter = freq_counter[1:]
    dmm = dmm[1:]
    timestamps = timestamps[1:]

    return freq_counter, dmm, timestamps

#the timestamps are stored as a string in the csv, so convert to number and then do math to get time change
def convertTimestampstoInterval(timestamps):
    #convert strings to floats
    for i in range(0, len(timestamps)):
        timestamps[i] = float(timestamps[i])
    #convert to time from start
    delta_times = getTimeIntervals(timestamps)
    return delta_times

def convertKSFreqstoFloat(freqs):
    freq_nums = []
    for i in range(0,len(freqs)):
        freq_nums.append(float(freqs[i]))
    return freq_nums 

def adjustKSfromDMM(ks, dmm):
    ks_adj = []
    for i in range(0, len(ks)):
        ks_adj.append(ks[i]+dmm[i])
    return ks_adj

def processAllData(filepath, metal, energy):
    freq_c, dmm_v, tstamps = getRawDataFromCSV(filepath)
    dmm_freqs = convertDMMData(dmm_v, metal, energy)
    t_ints = convertTimestampstoInterval(tstamps)
    freq_c = convertKSFreqstoFloat(freq_c)
    freq_c_adj = adjustKSfromDMM(freq_c, dmm_freqs)
    
    #make a data frame for these to live in

    df = pd.DataFrame({
        'Time': t_ints,
        'Keysight': freq_c,
        'DMM': dmm_freqs,
        'Adjusted Keysight Data': freq_c_adj
        
    })

    return df

def createCSVProcessedData(fp, data):
    data.to_csv(fp, mode='w', index=False, header=True)


def findDMMOverflowVals(data):
    rows = data[data['Voltages'] > 10000].index.tolist()
    return rows

def removeDMMOverflowVals(fp):
    data = pd.read_csv(fp)
    to_remove = findDMMOverflowVals(data)
    clean_data = data.drop(to_remove)
    return clean_data