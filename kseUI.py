import PySimpleGUI as sg
import pyvisa as visa
import kseDataCollection as dc

sg.theme('Light Blue 2')

rm = visa.ResourceManager()
resources = []
for r in rm.list_resources():
    resources.append(r)

#keysight_select = sg.Combo(resources, expand_x=True, enable_events=False, readonly=True, key='KeysightLocation')
#dmm_select = sg.Combo(resources, expand_x=True, enable_events=False, readonly=True, key='DMMLocation')


layout = [
    [sg.Text('Select your experimental parameters')],
    [sg.Text('Trigger Count'), sg.InputText(key='TriggerCount')],
    [sg.Text('Collection Time (s)'), sg.InputText(key='CollectionTime')],
    [sg.Text('Raw Data Filepath'), sg.FolderBrowse(key='RawDataPath')],
    [sg.Submit(), sg.Cancel()]
]

window = sg.Window('Testing things', layout)


while True:
    event, values = window.read()
    print(event, values)

    if (event == 'Submit'):
        dc.collectKSEData(float(values['TriggerCount']), float(values['CollectionTime']), values['RawDataPath'])

    if event in(sg.WINDOW_CLOSED, 'Exit', 'Cancel'):
        break

window.close()



