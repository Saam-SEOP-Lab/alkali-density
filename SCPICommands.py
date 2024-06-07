# this class will be used to build common commands used by instruments that accept SCPI language inputs

#Trigger Configuration
def setTrigSource(inst, source):
    #options: Immediate, External, Bus
    cmd = 'TRIG:SOUR '+ source
    inst.write(cmd)

def getTrigSource(inst):
    cmd = 'TRIG:SOUR?'
    reply = inst.query(cmd)
    return reply

def setTrigCount(inst, count):
    #count can be an integer between 1 and 1,000,000
    cmd = 'TRIG:COUN '+ str(count)
    inst.write(cmd)


#Measurement Type Config
def setMeasurementType(inst, measurement):
    cmd = 'CONF:'+measurement
    inst.write(cmd)

#frequency measurement configuration
def setFreqMode(inst, mode):
    cmd = 'SENS:FREQ:MODE '+ mode
    inst.write(cmd)

def getFreqMode(inst):
    cmd = 'SENS:FREQ:MODE?'
    reply = inst.query(cmd)
    return reply

#Gating Configuration
def setGatingTime(inst, t):
    cmd = 'SENS:FREQ:GATE:TIME '+str(t)
    inst.write(cmd)

def getGateTime(inst):
    cmd = 'SENS:FREQ:GATE:TIME?'
    reply = inst.query(cmd)
    return reply

def setGateSource(inst, source):
    #options are Time (TIME), external (EXT), Input 1 (INP1), Input 2 (INP2), Advanced (ADV)
    cmd = 'SENS:FREQ:GATE:SOUR '+ source
    inst.write(cmd)

def getGateSource(inst):
    cmd = 'SENS:FREQ:GATE:SOUR?'
    reply = inst.query(cmd)
    return reply

#Collecting data
def startCollection(inst):
    #note that sending the INIT command will clear any previous measurements from the instrument's memory
    #INIT also puts the system into 'wait for trigger' state, so this must run in order for data to be collected at all
    cmd = 'INIT'
    inst.write(cmd)


def getCollectedData(inst):
    #waits until all measurements finish to get the data
    #does not remove measurements from the instrument's memory when read
    cmd = 'FETC?'
    reply = inst.query(cmd)
    return reply


#Overall instance management
def clearAllRegisters(inst):
    cmd = '*CLS'
    inst.write(cmd)

def reset(inst):
    cmd = '*RST'
    inst.write(cmd)