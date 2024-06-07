import nidaqmx
import time

def getDAQlocalSystem():
    local_system = nidaqmx.system.System.local()
    return local_system

def getDAQDriverVersion():
    local_system = getDAQlocalSystem()
    driver_version = local_system.driver_version
    return driver_version

def listAllDAQs():
    local_system = getDAQlocalSystem()
    daqs = []
    for device in local_system.devices:
        daqs.append(device)
    return daqs
    
def getDAQMXInfo():
    driver_version = getDAQDriverVersion()
    daqmxinfo = "DAQmx {0}.{1}.{2}".format(
        driver_version.major_version,
        driver_version.minor_version,
        driver_version.update_version,
    )
    return daqmxinfo

def genAnalogTriggerCycle(task, num_triggers, high_V, low_V, high_time, low_time):
    i=0
    timestamps = []
    while (i<num_triggers):
        task.write(high_V) #high voltage value to send (probably stay below 5V in general)
        timestamps.append(time.time())
        time.sleep(high_time) #how long do we want to stay at the hight voltage
        task.write(low_V) #usually this will be 0V
        time.sleep(low_time) #how long do we want to stay at the low voltage
        i = i+1
    return timestamps



        