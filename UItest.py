import PySimpleGUI as sg
import pyvisa as visa


sg.theme('Light Blue 2')      # Add some color to the window

#want to turn this into a dropdown menu
rm = visa.ResourceManager()
resources = []
for r in rm.list_resources():
    resources.append(r)

instrument_select = sg.Combo(resources, font=('Arial Bold', 14),  expand_x=True, enable_events=True,  readonly=False, key='-COMBO-')

# Very basic window.  Return values using auto numbered keys

layout = [
    [sg.Text('Please enter your experiment collection parapmeters')],
    [sg.Text('Trigger Count', size=(20, 1)), sg.InputText()],
    [sg.Text('Collection Time (s)', size=(20, 1)), sg.InputText()],
    [sg.Text('Raw Data Filepath', size=(20, 1)), sg.Input(), sg.FolderBrowse()],
    [instrument_select],
    [sg.Submit(), sg.Cancel()]
]

window = sg.Window('Simple data entry window', layout)
event, values = window.read()
window.close()


# experiment settings that the user can enter
# as a dictionary
keys = ['TriggerCount', 
        'CollectionTime',
        'RawFilepath', 
        'InstrumentPath']

settings = dict.fromkeys(keys)

i=0
for key in keys: 
    settings[key] = values[i]
    i=i+1

print(settings)    # the input data looks like a simple list when auto numbered
